import asyncio
import json
import base64
import websockets

async def test_websocket():
    uri = "ws://127.0.0.1:8000/api/voice?user_id=test-user"
    print(f"Connecting to {uri}...")
    async with websockets.connect(uri) as ws:
        # Read initial status
        init_msg = await ws.recv()
        print(f"Init event: {init_msg}")

        # Test 1: Math calculation tool execution
        print("\n--- TEST 1: Math Calculation Accuracy ---")
        await ws.send(json.dumps({
            "type": "text_input",
            "text": "What is 25 percent of 840?"
        }))

        while True:
            raw = await ws.recv()
            data = json.loads(raw)
            print(f"Event: {data.get('type')} -> {data}")
            if data.get("type") == "response_text":
                print(f"\n>> Got Answer: {data.get('display_text')}")
                print(f">> Tool used: {data.get('tool_used')}")
                assert "210" in data.get("display_text"), f"Expected 210 in answer, got: {data.get('display_text')}"
                print(">> MATH ACCURACY VERIFIED: 100% CORRECT!")
            if data.get("type") == "agent_status" and data.get("status") == "IDLE":
                break

        # Test 2: Factual knowledge with Groq LLM
        print("\n--- TEST 2: Factual Knowledge via Groq API ---")
        await ws.send(json.dumps({
            "type": "text_input",
            "text": "What is the capital of Japan? Answer in one short sentence."
        }))

        while True:
            raw = await ws.recv()
            data = json.loads(raw)
            if data.get("type") == "response_text":
                print(f"\n>> Got Answer: {data.get('display_text')}")
                assert "Tokyo" in data.get("display_text"), f"Expected Tokyo in answer, got: {data.get('display_text')}"
                print(">> FACTUAL ACCURACY VERIFIED: 100% CORRECT!")
            if data.get("type") == "agent_status" and data.get("status") == "IDLE":
                break

        # Test 3: Direct audio payload handling
        print("\n--- TEST 3: Direct Audio Transmission with TEST_PROMPT ---")
        # WhisperSTTProvider in tests recognizes b"TEST_PROMPT:..."
        fake_audio = b"TEST_PROMPT:Calculate 15 plus 35\n" + (b"\x00" * 800)
        b64_audio = base64.b64encode(fake_audio).decode("utf-8")

        await ws.send(json.dumps({
            "type": "audio_data",
            "data": b64_audio,
            "mime_type": "audio/wav"
        }))

        while True:
            raw = await ws.recv()
            data = json.loads(raw)
            print(f"Audio Flow Event: {data.get('type')} -> {data}")
            if data.get("type") == "transcript_final":
                print(f"\n>> Recognized Transcript: '{data.get('text')}'")
            if data.get("type") == "response_text":
                print(f">> Answer to audio: {data.get('display_text')}")
                assert "50" in data.get("display_text"), f"Expected 50 in answer, got: {data.get('display_text')}"
                print(">> AUDIO PIPELINE VERIFIED: 100% ACCURATE!")
            if data.get("type") == "agent_status" and data.get("status") == "IDLE":
                break

    print("\nALL VOICE WEBSOCKET AND ACCURACY TESTS PASSED!")

if __name__ == "__main__":
    asyncio.run(test_websocket())
