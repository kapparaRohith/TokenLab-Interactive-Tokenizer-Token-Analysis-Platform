"""
Integration tests for all API routes.
Covers all success paths, all error paths, and SC-002 schema completeness.
"""
import io
import pytest

REQUIRED_RESULT_FIELDS = {
    "original_text", "source_type", "tokenizer", "encoding",
    "token_count", "tokens", "token_ids", "token_texts",
    "char_count", "word_count", "tokens_per_word", "tokens_per_char",
    "vocabulary", "new_token_ids",
}


class TestHealth:
    def test_health_ok(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


class TestEncodings:
    def test_returns_all_5_encodings(self, client):
        r = client.get("/tokenize/encodings")
        assert r.status_code == 200
        encodings = r.json()["encodings"]
        for name in ("cl100k_base", "p50k_base", "p50k_edit", "r50k_base", "o200k_base"):
            assert name in encodings

    def test_response_shape(self, client):
        r = client.get("/tokenize/encodings")
        assert "encodings" in r.json()


class TestTokenizeText:
    def test_tiktoken_valid_returns_200(self, client):
        r = client.post("/tokenize/text", data={
            "text": "Hello world!", "tokenizer": "tiktoken", "encoding": "cl100k_base"
        })
        assert r.status_code == 200

    def test_sc002_all_14_fields_present(self, client):
        """SC-002: all required fields must be present."""
        r = client.post("/tokenize/text", data={
            "text": "Hello world!", "tokenizer": "tiktoken", "encoding": "cl100k_base"
        })
        body = r.json()
        assert REQUIRED_RESULT_FIELDS.issubset(body.keys())

    def test_token_count_matches_tokens_list(self, client):
        r = client.post("/tokenize/text", data={
            "text": "Hello world!", "tokenizer": "tiktoken", "encoding": "cl100k_base"
        })
        body = r.json()
        assert body["token_count"] == len(body["tokens"])
        assert body["token_count"] == len(body["token_ids"])

    def test_tiktoken_empty_text_returns_400(self, client):
        r = client.post("/tokenize/text", data={
            "text": "   ", "tokenizer": "tiktoken", "encoding": "cl100k_base"
        })
        assert r.status_code == 400
        assert "empty" in r.json()["detail"].lower()

    def test_tiktoken_missing_encoding_returns_400(self, client):
        r = client.post("/tokenize/text", data={
            "text": "hello", "tokenizer": "tiktoken"
        })
        assert r.status_code == 400
        assert "encoding" in r.json()["detail"].lower()

    def test_tiktoken_unsupported_encoding_returns_400(self, client):
        r = client.post("/tokenize/text", data={
            "text": "hello", "tokenizer": "tiktoken", "encoding": "gpt2"
        })
        assert r.status_code == 400
        assert "gpt2" in r.json()["detail"]

    def test_missing_tokenizer_field_returns_422(self, client):
        r = client.post("/tokenize/text", data={"text": "hello"})
        assert r.status_code == 422

    def test_custom_returns_vocabulary_and_new_ids(self, client):
        r = client.post("/tokenize/text", data={"text": "Hello world!", "tokenizer": "custom"})
        assert r.status_code == 200
        body = r.json()
        assert body["vocabulary"] is not None
        assert body["new_token_ids"] is not None

    def test_custom_second_call_no_new_ids(self, client):
        client.post("/tokenize/text", data={"text": "Hello world!", "tokenizer": "custom"})
        r = client.post("/tokenize/text", data={"text": "Hello world!", "tokenizer": "custom"})
        body = r.json()
        assert body["new_token_ids"] == []
        assert all(not e["is_new"] for e in body["vocabulary"])

    def test_custom_second_call_doubled_frequencies(self, client):
        client.post("/tokenize/text", data={"text": "Hello world!", "tokenizer": "custom"})
        r = client.post("/tokenize/text", data={"text": "Hello world!", "tokenizer": "custom"})
        body = r.json()
        assert all(e["frequency"] == 2 for e in body["vocabulary"])

    def test_tiktoken_vocabulary_is_null(self, client):
        r = client.post("/tokenize/text", data={
            "text": "hello", "tokenizer": "tiktoken", "encoding": "cl100k_base"
        })
        assert r.json()["vocabulary"] is None
        assert r.json()["new_token_ids"] is None

    @pytest.mark.parametrize("encoding", [
        "cl100k_base", "p50k_base", "p50k_edit", "r50k_base", "o200k_base"
    ])
    def test_all_encodings_return_200(self, client, encoding):
        r = client.post("/tokenize/text", data={
            "text": "Hello", "tokenizer": "tiktoken", "encoding": encoding
        })
        assert r.status_code == 200

    def test_error_detail_is_string_not_object(self, client):
        r = client.post("/tokenize/text", data={
            "text": "   ", "tokenizer": "tiktoken", "encoding": "cl100k_base"
        })
        assert isinstance(r.json()["detail"], str)


class TestTokenizeFile:
    def test_txt_file_returns_200(self, client, sample_txt_bytes):
        r = client.post("/tokenize/file", data={
            "tokenizer": "tiktoken", "encoding": "cl100k_base"
        }, files={"file": ("test.txt", sample_txt_bytes, "text/plain")})
        assert r.status_code == 200
        body = r.json()
        assert body["source_type"] == "txt"
        assert "Hello" in body["original_text"]

    def test_pdf_file_returns_200(self, client, sample_pdf_bytes):
        r = client.post("/tokenize/file", data={
            "tokenizer": "tiktoken", "encoding": "cl100k_base"
        }, files={"file": ("test.pdf", sample_pdf_bytes, "application/pdf")})
        assert r.status_code == 200
        assert r.json()["source_type"] == "pdf"

    def test_unsupported_type_returns_400(self, client):
        r = client.post("/tokenize/file", data={
            "tokenizer": "tiktoken", "encoding": "cl100k_base"
        }, files={"file": ("test.docx", b"data", "application/octet-stream")})
        assert r.status_code == 400
        assert "Unsupported" in r.json()["detail"]

    def test_oversized_file_returns_413(self, client):
        big = b"x" * (10 * 1024 * 1024 + 1)
        r = client.post("/tokenize/file", data={
            "tokenizer": "tiktoken", "encoding": "cl100k_base"
        }, files={"file": ("big.txt", big, "text/plain")})
        assert r.status_code == 413

    def test_empty_txt_returns_400(self, client):
        r = client.post("/tokenize/file", data={
            "tokenizer": "tiktoken", "encoding": "cl100k_base"
        }, files={"file": ("empty.txt", b"   ", "text/plain")})
        assert r.status_code == 400

    def test_corrupt_pdf_returns_400(self, client, corrupt_pdf_bytes):
        r = client.post("/tokenize/file", data={
            "tokenizer": "tiktoken", "encoding": "cl100k_base"
        }, files={"file": ("bad.pdf", corrupt_pdf_bytes, "application/pdf")})
        assert r.status_code == 400
        assert "corrupted" in r.json()["detail"].lower()

    def test_image_only_pdf_returns_400(self, client, empty_pdf_bytes):
        r = client.post("/tokenize/file", data={
            "tokenizer": "tiktoken", "encoding": "cl100k_base"
        }, files={"file": ("empty.pdf", empty_pdf_bytes, "application/pdf")})
        assert r.status_code == 400
        assert "No extractable" in r.json()["detail"]


class TestCustomReset:
    def test_reset_returns_200(self, client):
        r = client.post("/tokenize/custom/reset")
        assert r.status_code == 200
        assert "reset" in r.json()["message"].lower()

    def test_after_reset_tokens_are_new(self, client):
        client.post("/tokenize/text", data={"text": "hello world", "tokenizer": "custom"})
        client.post("/tokenize/custom/reset")
        r = client.post("/tokenize/text", data={"text": "hello world", "tokenizer": "custom"})
        body = r.json()
        assert all(e["is_new"] for e in body["vocabulary"])
