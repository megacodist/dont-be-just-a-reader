"""Decorator design pattern is used to create a package which supports
adding of functionalities either at the beginning or end. Here we want
to add notifying mechanisms so we can use different sets of alerting
methods based on recepient.
The INotifier interface and AbstractNotifier abstract class combination
is a good design of a class which can reference itself.
"""

from abc import ABC, abstractmethod


class INotifier(ABC):
	@abstractmethod
	def send(self, msg : str) -> None:
		pass

	@abstractmethod
	def trigger(self, msg : str) -> None:
		pass


class AbstractNotifier(INotifier):
	def __init__(
			self,
			notifier: INotifier = None
			) -> None:
		self._prev = notifier

	@abstractmethod
	def send(self, msg : str) -> None:
		pass

	def trigger(self, msg : str) -> None:
		self.send(msg)
		if self._prev is not None:
			self._prev.trigger(msg)


class EmailNotifier(AbstractNotifier):
	def send(self, msg : str) -> None:
		print(f"'{msg}' was sent to the email")


class SlackNotifier(AbstractNotifier):
	def send(self, msg : str) -> None:
		print(f'{msg} was written in a Slack post')


class VoiceNotifier(AbstractNotifier):
	def send(self, msg : str) -> None:
		print(f"'{msg}' was said in a voice call")


class SmsNotifier(AbstractNotifier):
	def send(self, msg : str) -> None:
		print(f"'{msg}' was sent in an SMS")


if __name__ == '__main__':
	notifier = VoiceNotifier()
	notifier = EmailNotifier(notifier)
	notifier = SmsNotifier(notifier)
	notifier.trigger('Hello World')
	del notifier
	notifier = SmsNotifier()
	notifier = VoiceNotifier(notifier)
	notifier.trigger('Hi Pythonistas')
