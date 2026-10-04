class ModelError(Exception):
	pass

class ModelTimeoutError(ModelError):
	pass

class ModelAdapter:
	def __init__(self, transport):
		self.transport = transport
	def complete(self, prompt: str, timeout_seconds: float = 30.0) -> str:
		return self.transport(prompt, timeout_seconds)


