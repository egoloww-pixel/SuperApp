from PySide6.QtCore import QObject, Signal


class AppCore(QObject):
    """Ядро: хранит модули и предоставляет шину событий."""

    module_registered = Signal(str)   # id модуля
    event_bus = Signal(str, object)   # (топик, payload)

    def __init__(self):
        super().__init__()
        self._modules = {}

    def register(self, module_cls):
        mod = module_cls()
        self._modules[mod.id] = mod
        self.module_registered.emit(mod.id)
        return mod

    def modules(self):
        return list(self._modules.values())

    def get(self, module_id: str):
        return self._modules.get(module_id)

    def publish(self, topic: str, payload=None):
        self.event_bus.emit(topic, payload)
