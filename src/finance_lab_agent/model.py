from math import isfinite


class ModelError(Exception):
	pass

class ModelTimeoutError(ModelError):
	pass

class ModelAdapter:
	def __init__(self, transport):
		self.transport = transport
	def complete(self, prompt: str, timeout_seconds: float = 30.0) -> str:
		if not prompt.strip():
			raise ValueError("prompt must not be empty")
		if not isfinite(timeout_seconds) or timeout_seconds <= 0:
			raise ValueError("timeout_seconds must be positive and finite")
		try:
			return self.transport(prompt, timeout_seconds)
		except TimeoutError as error:
			raise ModelTimeoutError(str(error)) from error
		except ModelError:
			raise
		except Exception as error:
			raise ModelError(str(error)) from error
