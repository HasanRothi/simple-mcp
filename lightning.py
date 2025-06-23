from pydantic import BaseModel
from litserve.mcp import MCP
import litserve as ls


class TextClassificationRequest(BaseModel):
    input: str


class TextClassificationAPI(ls.LitAPI):
    def setup(self, device):
        # You can initialize a dummy variable or load custom logic
        self.device = device

    def decode_request(self, request: TextClassificationRequest):
        return request.input

    def predict(self, x):
        # Dummy logic for sentiment classification
        if "good" in x.lower():
            return {"label": "POSITIVE", "score": 0.99}
        else:
            return {"label": "NEGATIVE", "score": 0.85}

    def encode_response(self, output):
        return output


if __name__ == "__main__":
    api = TextClassificationAPI(mcp=MCP(description="Dummy sentiment classifier"))
    server = ls.LitServer(api)
    server.run(port=8000)
