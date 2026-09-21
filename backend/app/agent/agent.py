import logging
from typing import Optional, List, Dict, Any, AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.agent.state import AgentState, AgentStatus
from app.agent.prompts import build_agent_prompt, NOVA_SYSTEM_PROMPT
from app.providers.llm import get_llm_provider
from app.database.models import Conversation, Message, Memory

logger = logging.getLogger("nova.agent")


class NovaAgent:
    """Core Agent Orchestrator for NOVA."""

    def __init__(self, db: AsyncSession, user_id: Optional[str] = None):
        self.db = db
        self.user_id = user_id
        self.llm_provider = get_llm_provider()
        self.state = AgentState(user_id=user_id, agent_status=AgentStatus.IDLE)

    @staticmethod
    def _parse_display_and_spoken(text: str) -> tuple[str, str]:
        if not text:
            return "", ""
        import re
        match = re.search(r"\*{0,2}Spoken(?:\s+Text)?\*{0,2}[:\s]+([\s\S]+)$", text, re.IGNORECASE)
        if match:
            spoken = match.group(1).strip()
            display = text[:match.start()].strip()
            display = re.sub(r"^\*{0,2}Display(?:\s+Text)?\*{0,2}[:\s]*", "", display, flags=re.IGNORECASE).strip()
            display = re.sub(r"[\*-]{3,}\s*$", "", display).strip()
            if not display:
                display = spoken
            return display, spoken
        return text, text

    async def _load_history(self, conversation_id: str, limit: int = 10) -> List[Dict[str, str]]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        messages = res.scalars().all()
        history = []
        for m in reversed(messages):
            role = "user" if m.sender == "user" else "assistant"
            history.append({"role": role, "content": m.content})
        return history

    async def _retrieve_memories(self, query: str = "") -> List[Dict[str, Any]]:
        if not self.user_id:
            return []
        from app.memory.long_term import LongTermMemoryManager
        mgr = LongTermMemoryManager(db=self.db, user_id=self.user_id)
        return await mgr.get_relevant_memories(query=query, limit=5)

    async def _retrieve_documents(self, query: str = "") -> List[Dict[str, Any]]:
        if not self.user_id:
            return []
        from app.rag.retrieval import RAGRetriever
        retriever = RAGRetriever(db=self.db, user_id=self.user_id)
        return await retriever.retrieve(query=query, top_k=3)

    async def process_multimodal_event(
        self,
        event,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process any modality structured UserInputEvent."""
        from app.agent.multimodal import MultimodalNormalizer
        normalizer = MultimodalNormalizer()
        normalized = await normalizer.normalize(event)

        result = await self.process_text(
            text=normalized["normalized_prompt"],
            conversation_id=conversation_id,
        )
        result["modality"] = normalized["modality"]
        result["sensory_data"] = normalized["sensory_data"]
        return result

    async def _extract_and_save_memories(self, text: str):
        if not self.user_id:
            return
        from app.memory.long_term import LongTermMemoryManager
        mgr = LongTermMemoryManager(db=self.db, user_id=self.user_id)
        extracted = mgr.extract_memories(text)
        for item in extracted:
            await mgr.save_memory(
                category=item["category"],
                key=item["key"],
                value=item["value"],
            )

    async def process_text(
        self,
        text: str,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Synchronous/standard turn execution with tool planning."""
        self.state.agent_status = AgentStatus.THINKING
        import uuid
        import datetime
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        self.state.conversation_id = conversation_id

        # 1. Ensure conversation exists with clean title
        res = await self.db.execute(select(Conversation).where(Conversation.id == conversation_id))
        conv = res.scalar_one_or_none()
        if not conv:
            title = text.strip()
            if len(title) > 38:
                title = title[:35] + "..."
            conv = Conversation(
                id=conversation_id,
                user_id=self.user_id or "user-default",
                title=title or "New Conversation",
            )
            self.db.add(conv)
            await self.db.commit()
        else:
            conv.updated_at = datetime.datetime.now(datetime.timezone.utc)
            await self.db.commit()

        # 2. Persist user message and extract long-term facts
        user_msg = Message(
            conversation_id=conversation_id,
            sender="user",
            content=text,
        )
        self.db.add(user_msg)
        await self.db.commit()

        await self._extract_and_save_memories(text)

        # 3. Tool Planning & Decision
        from app.agent.planner import AgentPlanner
        planner = AgentPlanner(db=self.db, user_id=self.user_id)
        tool_name, tool_result, awaiting_confirmation, conf_prompt = await planner.plan_and_execute(
            user_input=text,
            conversation_id=conversation_id,
        )

        if awaiting_confirmation and conf_prompt:
            self.state.awaiting_confirmation = True
            self.state.confirmation_prompt = conf_prompt
            self.state.agent_status = AgentStatus.IDLE
            display_text = conf_prompt
            spoken_text = conf_prompt
            if conversation_id:
                agent_msg = Message(
                    conversation_id=conversation_id,
                    sender="agent",
                    content=display_text,
                    spoken_content=spoken_text,
                )
                self.db.add(agent_msg)
                await self.db.commit()
            return {
                "conversation_id": conversation_id,
                "display_text": display_text,
                "spoken_text": spoken_text,
                "agent_status": self.state.agent_status.value,
                "awaiting_confirmation": True,
            }

        if tool_name and tool_result and tool_result.get("status") == "completed":
            self.state.agent_status = AgentStatus.USING_TOOL
            self.state.active_tool = tool_name
            self.state.tool_results.append(tool_result)

            # Format concise voice-first spoken response directly from verified tool result
            res_val = tool_result.get("result")
            if tool_name == "calculator":
                ans = res_val.get("result")
                display_text = f"The answer is {ans}."
                spoken_text = f"It's {ans}."
            elif tool_name == "weather":
                loc = res_val.get("location")
                temp = res_val.get("temperature_c")
                cond = res_val.get("condition")
                display_text = f"The weather in {loc} is {temp}°C with {cond}."
                spoken_text = f"In {loc}, it's currently {temp} degrees Celsius and {cond}."
            elif tool_name == "web_search":
                query = res_val.get("query", "your query")
                results = res_val.get("results", [])

                if not results:
                    display_text = "I couldn't find any recent information on that."
                    spoken_text = display_text
                else:
                    # Gather top snippets for fast direct synthesis
                    snippets = []
                    for r in results[:4]:
                        snip = r.get("snippet", "").strip()
                        if snip:
                            snippets.append(snip)
                    context_text = "\n".join(snippets)[:1200]

                    # Fast direct synthesis: answer user prompt directly without mentioning search, browsing, or URLs
                    synth_prompt = (
                        f"Context information:\n{context_text}\n\n"
                        f"User question: {text}\n\n"
                        f"Answer the user's question directly and concisely in 1 to 2 clear sentences. "
                        f"CRITICAL RULES:\n"
                        f"- Respond in the EXACT SAME language that the user asked in (e.g. Hindi, Spanish, French, German, etc.).\n"
                        f"- Do NOT say 'I searched online', 'according to the search', or mention search engines.\n"
                        f"- Do NOT list links, URLs, or citations.\n"
                        f"- Speak naturally and directly to the point."
                    )
                    try:
                        direct_answer = await self.llm_provider.generate(
                            [
                                {
                                    "role": "system",
                                    "content": "You are NOVA, a voice agent. Answer user questions directly, naturally, and concisely in 1-2 sentences. Never mention search engines, searching online, browsing, or URLs.",
                                },
                                {"role": "user", "content": synth_prompt},
                            ],
                            temperature=0.2,
                        )
                        direct_answer = direct_answer.strip()
                    except Exception as e:
                        logger.warning(f"Fast LLM synthesis of search results failed: {e}")
                        import re as _re
                        top_snip = snippets[0] if snippets else "I don't have details on that right now."
                        sentences = _re.split(r"(?<=[.!?])\s+", top_snip)
                        direct_answer = " ".join(sentences[:2]).strip()

                    display_text = direct_answer
                    spoken_text = direct_answer
            else:
                display_text = f"Tool '{tool_name}' executed successfully: {res_val}"
                spoken_text = display_text

            self.state.agent_status = AgentStatus.IDLE
            if conversation_id:
                agent_msg = Message(
                    conversation_id=conversation_id,
                    sender="agent",
                    content=display_text,
                    spoken_content=spoken_text,
                )
                self.db.add(agent_msg)
                await self.db.commit()

            return {
                "conversation_id": conversation_id,
                "display_text": display_text,
                "spoken_text": spoken_text,
                "agent_status": self.state.agent_status.value,
                "tool_used": tool_name,
            }

        # 4. Standard LLM Reasoning if no tool was required
        history = []
        if conversation_id:
            history = await self._load_history(conversation_id)
        memories = await self._retrieve_memories(query=text)
        retrieved_docs = await self._retrieve_documents(query=text)

        system_message = build_agent_prompt(
            system_prompt=NOVA_SYSTEM_PROMPT,
            memories=memories,
            retrieved_documents=retrieved_docs,
        )

        llm_messages = [{"role": "system", "content": system_message}] + history
        if not history or history[-1]["content"] != text:
            llm_messages.append({"role": "user", "content": text})

        self.state.agent_status = AgentStatus.GENERATING
        try:
            full_response = await self.llm_provider.generate(llm_messages)
        except Exception as e:
            logger.error(f"Error calling LLM provider: {e}", exc_info=True)
            self.state.agent_status = AgentStatus.ERROR
            self.state.error_message = str(e)
            full_response = "I encountered an error connecting to my reasoning service. Please try again."

        display_text, spoken_text = self._parse_display_and_spoken(full_response)

        # 5. Persist agent message
        if conversation_id:
            agent_msg = Message(
                conversation_id=conversation_id,
                sender="agent",
                content=display_text,
                spoken_content=spoken_text,
            )
            self.db.add(agent_msg)
            await self.db.commit()

        self.state.agent_status = AgentStatus.IDLE

        return {
            "conversation_id": conversation_id,
            "display_text": display_text,
            "spoken_text": spoken_text,
            "agent_status": self.state.agent_status.value,
        }

    async def stream_text(
        self,
        text: str,
        conversation_id: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """Stream response tokens for low-latency delivery."""
        self.state.agent_status = AgentStatus.THINKING
        self.state.conversation_id = conversation_id

        # Load history and memories
        history = []
        if conversation_id:
            history = await self._load_history(conversation_id)
        memories = await self._retrieve_memories()

        system_message = build_agent_prompt(
            system_prompt=NOVA_SYSTEM_PROMPT,
            memories=memories,
        )

        llm_messages = [{"role": "system", "content": system_message}] + history
        llm_messages.append({"role": "user", "content": text})

        self.state.agent_status = AgentStatus.GENERATING
        accumulated = []
        try:
            async for token in self.llm_provider.stream_generate(llm_messages):
                accumulated.append(token)
                yield token
        finally:
            full_text = "".join(accumulated)
            if conversation_id and full_text:
                agent_msg = Message(
                    conversation_id=conversation_id,
                    sender="agent",
                    content=full_text,
                    spoken_content=full_text,
                )
                self.db.add(agent_msg)
                await self.db.commit()
            self.state.agent_status = AgentStatus.IDLE
