"""
AI可视化调试工具 —— 基于三元框架（TEF）的模式联奏实现
- 地方（Model层）：单例模式 + 观察者模式
- 人和（View层）：组合模式 + 中介者模式
- 天圆（Controller层）：命令模式 + 撤销/重做
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Set
from datetime import datetime
import threading
import json


# ==================== 地方（Model层）：稳定与一致 ====================

class ModelObserver(ABC):
    """观察者接口"""
    @abstractmethod
    def on_model_update(self, event_type: str, data: Any):
        pass


class AIDataModel:
    """
    AI数据模型 - 单例模式确保数据一致性
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._training_data = {}
        self._model_parameters = {}
        self._training_history = []
        self._current_epoch = 0
        self._observers: Set[ModelObserver] = set()
        self._initialized = True

    # 观察者模式：管理监听者
    def add_observer(self, observer: ModelObserver):
        self._observers.add(observer)

    def remove_observer(self, observer: ModelObserver):
        self._observers.discard(observer)

    def _notify_observers(self, event_type: str, data: Any = None):
        for observer in self._observers:
            observer.on_model_update(event_type, data)

    # 地方核心：稳定的数据操作
    def update_model_parameters(self, params: Dict[str, Any]):
        self._model_parameters.update(params)
        self._notify_observers("parameters_updated", params)

    def add_training_record(self, record: Dict[str, Any]):
        record['timestamp'] = datetime.now().isoformat()
        record['epoch'] = self._current_epoch
        self._training_history.append(record)
        self._current_epoch += 1
        self._notify_observers("training_progress", record)

    def get_training_summary(self) -> Dict[str, Any]:
        return {
            "total_epochs": self._current_epoch,
            "latest_loss": self._training_history[-1]['loss'] if self._training_history else 0,
            "parameter_count": len(self._model_parameters)
        }


# ==================== 人和（View层）：灵活与协作 ====================

class UIComponent(ABC):
    """组合模式：组件抽象"""
    def __init__(self, name: str):
        self.name = name
        self.mediator = None

    def set_mediator(self, mediator):
        self.mediator = mediator

    @abstractmethod
    def render(self) -> str:
        pass

    @abstractmethod
    def handle_event(self, event: str, data: Any = None):
        pass


class LeafComponent(UIComponent):
    """叶子组件（具体控件）"""
    def __init__(self, name: str, component_type: str):
        super().__init__(name)
        self.component_type = component_type
        self.state = {}

    def render(self) -> str:
        return f"{self.component_type}: {self.name}"

    def handle_event(self, event: str, data: Any = None):
        if self.mediator:
            self.mediator.notify(self, event, data)


class CompositeComponent(UIComponent):
    """复合组件（容器）"""
    def __init__(self, name: str):
        super().__init__(name)
        self.children: List[UIComponent] = []

    def add(self, component: UIComponent):
        component.set_mediator(self.mediator)
        self.children.append(component)

    def render(self) -> str:
        lines = [f"Composite: {self.name}"]
        for child in self.children:
            lines.append(f"  - {child.render()}")
        return "\n".join(lines)

    def handle_event(self, event: str, data: Any = None):
        for child in self.children:
            child.handle_event(event, data)


class ViewMediator:
    """中介者模式：协调所有UI组件交互"""
    def __init__(self):
        self.components: Dict[str, UIComponent] = {}
        self.controller = None

    def register_component(self, name: str, component: UIComponent):
        component.set_mediator(self)
        self.components[name] = component

    def set_controller(self, controller):
        self.controller = controller

    def notify(self, sender: UIComponent, event: str, data: Any = None):
        print(f"[Mediator] {sender.name} 触发事件: {event}")
        if event == "parameter_changed":
            self.controller.update_model_parameters(data)
        elif event == "start_training":
            self.controller.start_training(data)
        elif event == "undo":
            self.controller.undo()
        elif event == "redo":
            self.controller.redo()


class AIDashboardView:
    """主视图：构建UI组件树并注册到中介者"""
    def __init__(self):
        self.mediator = ViewMediator()
        self._build_ui()

    def _build_ui(self):
        # 创建叶子组件
        param_panel = LeafComponent("param_panel", "ParameterPanel")
        train_btn = LeafComponent("train_btn", "Button")
        loss_chart = LeafComponent("loss_chart", "LineChart")
        acc_chart = LeafComponent("acc_chart", "LineChart")

        # 注册到中介者
        for comp in [param_panel, train_btn, loss_chart, acc_chart]:
            self.mediator.register_component(comp.name, comp)

        # 构建复合组件树
        ctrl_panel = CompositeComponent("ControlPanel")
        ctrl_panel.add(param_panel)
        ctrl_panel.add(train_btn)

        viz_panel = CompositeComponent("VisualizationPanel")
        viz_panel.add(loss_chart)
        viz_panel.add(acc_chart)

        main_panel = CompositeComponent("MainPanel")
        main_panel.add(ctrl_panel)
        main_panel.add(viz_panel)

        self.root = main_panel

    def render(self) -> str:
        return self.root.render()

    def get_mediator(self) -> ViewMediator:
        return self.mediator

    def set_controller(self, controller):
        self.mediator.set_controller(controller)


# ==================== 天圆（Controller层）：规则与控制 ====================

class Command(ABC):
    @abstractmethod
    def execute(self) -> bool:
        pass

    @abstractmethod
    def undo(self) -> bool:
        pass


class TrainingCommand(Command):
    """训练命令"""
    def __init__(self, controller, training_config: Dict[str, Any]):
        self.controller = controller
        self.config = training_config
        self.previous_state = None

    def execute(self) -> bool:
        self.previous_state = self.controller.get_training_state()
        return self.controller._do_train(self.config)

    def undo(self) -> bool:
        if self.previous_state:
            return self.controller._restore_state(self.previous_state)
        return False


class ParameterUpdateCommand(Command):
    """参数更新命令"""
    def __init__(self, controller, params: Dict[str, Any]):
        self.controller = controller
        self.new_params = params
        self.old_params = {}

    def execute(self) -> bool:
        model = self.controller.model
        for k in self.new_params:
            self.old_params[k] = model._model_parameters.get(k)
        model.update_model_parameters(self.new_params)
        return True

    def undo(self) -> bool:
        if self.old_params:
            self.controller.model.update_model_parameters(self.old_params)
            return True
        return False


class CommandHistory:
    """撤销/重做栈"""
    def __init__(self):
        self.undo_stack: List[Command] = []
        self.redo_stack: List[Command] = []

    def execute(self, cmd: Command) -> bool:
        if cmd.execute():
            self.undo_stack.append(cmd)
            self.redo_stack.clear()
            return True
        return False

    def undo(self) -> bool:
        if not self.undo_stack:
            return False
        cmd = self.undo_stack.pop()
        if cmd.undo():
            self.redo_stack.append(cmd)
            return True
        return False

    def redo(self) -> bool:
        if not self.redo_stack:
            return False
        cmd = self.redo_stack.pop()
        if cmd.execute():
            self.undo_stack.append(cmd)
            return True
        return False


class AIController(ModelObserver):
    """
    天圆核心：协调 Model 与 View，封装命令，实现可回溯的控制逻辑
    """
    def __init__(self, model: AIDataModel, view: AIDashboardView):
        self.model = model
        self.view = view
        self.history = CommandHistory()
        # 建立双向连接
        self.model.add_observer(self)
        self.view.set_controller(self)

    # 观察者响应：当Model变化时，自动刷新View（此处仅打印，实际可调用中介者更新UI）
    def on_model_update(self, event_type: str, data: Any):
        if event_type == "training_progress":
            print(f"[Controller] 训练进度: epoch {data.get('epoch')}, loss {data.get('loss')}")
        elif event_type == "parameters_updated":
            print(f"[Controller] 参数已更新: {data}")

    # 对外命令接口
    def update_model_parameters(self, params: Dict[str, Any]):
        cmd = ParameterUpdateCommand(self, params)
        self.history.execute(cmd)

    def start_training(self, config: Dict[str, Any]):
        cmd = TrainingCommand(self, config)
        self.history.execute(cmd)

    def undo(self):
        self.history.undo()

    def redo(self):
        self.history.redo()

    # 内部训练逻辑（供Command调用）
    def _do_train(self, config: Dict[str, Any]) -> bool:
        epochs = config.get('epochs', 5)
        print(f"[Controller] 开始训练，epochs={epochs}")
        for epoch in range(epochs):
            # 模拟训练过程
            loss = 1.0 / (epoch + 1)
            acc = min(0.95, epoch * 0.1)
            record = {'epoch': epoch, 'loss': loss, 'accuracy': acc}
            self.model.add_training_record(record)
        return True

    def get_training_state(self) -> Dict[str, Any]:
        return {
            'history': self.model._training_history.copy(),
            'epoch': self.model._current_epoch
        }

    def _restore_state(self, state: Dict[str, Any]) -> bool:
        self.model._training_history = state['history']
        self.model._current_epoch = state['epoch']
        self.model._notify_observers("state_restored", state)
        return True


# ==================== 演示入口 ====================

def run_ai_visualization_tool():
    print("=" * 50)
    print("AI可视化调试工具 - 基于三元框架的模式联奏演示")
    print("=" * 50)

    # 1. 创建三元组件
    model = AIDataModel()           # 地方
    view = AIDashboardView()        # 人和
    controller = AIController(model, view)  # 天圆

    # 2. 展示初始界面（组合模式渲染）
    print("\n【界面结构】")
    print(view.render())

    # 3. 用户交互模拟：修改参数
    print("\n【用户操作】修改模型参数")
    param_panel = view.mediator.components['param_panel']
    param_panel.handle_event("parameter_changed", {'learning_rate': 0.01, 'batch_size': 32})

    # 4. 用户操作：开始训练
    print("\n【用户操作】开始训练")
    train_btn = view.mediator.components['train_btn']
    train_btn.handle_event("start_training", {'epochs': 3})

    # 5. 查看训练摘要
    print("\n【训练摘要】")
    print(model.get_training_summary())

    # 6. 撤销/重做演示
    print("\n【用户操作】撤销上一次训练")
    undo_btn = LeafComponent("undo_btn", "Button")
    view.mediator.register_component("undo_btn", undo_btn)
    undo_btn.handle_event("undo", None)

    print("\n【用户操作】重做")
    redo_btn = LeafComponent("redo_btn", "Button")
    view.mediator.register_component("redo_btn", redo_btn)
    redo_btn.handle_event("redo", None)

    print("\n演示结束。")


if __name__ == "__main__":
    run_ai_visualization_tool()
