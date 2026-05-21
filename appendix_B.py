"""
科学计算工作流引擎 —— 基于三元框架（TEF）的模式联奏实现
- 地方（流程骨架）：模板方法模式
- 天圆（算法与组件）：抽象工厂模式 + 策略模式 + 装饰器模式
- 人和（组件集成）：工厂 + 装饰器链组装函数
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
import time
import hashlib
import json
import os
import pickle


# ==================== 地方（流程骨架）：模板方法模式 ====================

class ScientificWorkflow(ABC):
    """科学计算工作流基类 - 模板方法模式定义不可变流程骨架"""

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """模板方法：固定执行顺序，子类不可覆写"""
        try:
            self._validate_input(input_data)
            processed = self._preprocess_data(input_data)
            result = self._perform_computation(processed)
            final_result = self._postprocess_result(result)
            self._validate_result(final_result)
            return final_result
        except Exception as e:
            return self._handle_error(e, input_data)

    def _validate_input(self, input_data: Dict[str, Any]):
        if not input_data:
            raise ValueError("输入数据不能为空")
        print("✓ 输入验证通过")

    @abstractmethod
    def _preprocess_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _perform_computation(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def _postprocess_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        result['processed_at'] = datetime.now().isoformat()
        print("✓ 结果后处理完成")
        return result

    def _validate_result(self, result: Dict[str, Any]):
        if 'error' in result:
            raise ValueError(f"计算结果包含错误: {result['error']}")
        print("✓ 结果验证通过")

    def _handle_error(self, error: Exception, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'error': str(error),
            'error_type': type(error).__name__,
            'input_data': input_data,
            'timestamp': datetime.now().isoformat()
        }


class NumericalSimulationWorkflow(ScientificWorkflow):
    """数值模拟工作流 - 具体实现"""
    def _preprocess_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        print("执行数值模拟数据预处理...")
        processed = input_data.copy()
        if 'parameters' in processed:
            for k, v in processed['parameters'].items():
                if isinstance(v, (int, float)):
                    processed['parameters'][k] = float(v)
        processed['simulation_id'] = hashlib.md5(
            json.dumps(processed, sort_keys=True).encode()
        ).hexdigest()[:8]
        return processed

    def _perform_computation(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        print("执行数值模拟计算...")
        time.sleep(0.05)  # 模拟计算耗时
        return {
            'simulation_id': processed_data['simulation_id'],
            'convergence_rate': 0.95,
            'iterations': 1000,
            'final_residual': 1e-6,
        }


class DataAnalysisWorkflow(ScientificWorkflow):
    """数据分析工作流"""
    def _preprocess_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        print("执行数据分析预处理...")
        processed = input_data.copy()
        if 'dataset' in processed:
            processed['cleaned_dataset'] = f"cleaned_{processed['dataset']}"
        return processed

    def _perform_computation(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        print("执行数据分析计算...")
        time.sleep(0.03)
        return {
            'statistics': {'mean': 0.5, 'std_dev': 0.1, 'correlation': 0.8},
            'insights': ['趋势上升', '周期性变化']
        }


# ==================== 天圆（算法与组件）：抽象工厂 + 策略 + 装饰器 ====================

# ---------- 策略模式：数值算法可插拔 ----------
class NumericalAlgorithm(ABC):
    @abstractmethod
    def solve(self, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        pass


class FiniteElementMethod(NumericalAlgorithm):
    def solve(self, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        print(" 使用有限元法求解")
        return {'method': 'FEM', 'converged': True, 'element_count': problem_data.get('elements', 1000)}
    def get_info(self) -> Dict[str, Any]:
        return {'name': '有限元法', 'suitable_for': ['结构分析', '热传导']}


class FiniteDifferenceMethod(NumericalAlgorithm):
    def solve(self, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        print(" 使用有限差分法求解")
        return {'method': 'FDM', 'converged': True, 'grid_points': problem_data.get('grid_points', 500)}
    def get_info(self) -> Dict[str, Any]:
        return {'name': '有限差分法', 'suitable_for': ['波动方程', '扩散问题']}


class SpectralMethod(NumericalAlgorithm):
    def solve(self, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        print(" 使用谱方法求解")
        return {'method': 'Spectral', 'converged': True, 'modes': problem_data.get('modes', 64)}
    def get_info(self) -> Dict[str, Any]:
        return {'name': '谱方法', 'suitable_for': ['周期问题', '高精度需求']}


class AlgorithmContext:
    """策略上下文 - 简化调用"""
    def __init__(self, algorithm: NumericalAlgorithm = None):
        self._algorithm = algorithm
    def set_algorithm(self, algorithm: NumericalAlgorithm):
        self._algorithm = algorithm
    def execute(self, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self._algorithm:
            raise ValueError("未设置算法")
        return self._algorithm.solve(problem_data)


# ---------- 装饰器模式：动态增强工作流 ----------
class WorkflowDecorator(ScientificWorkflow):
    def __init__(self, workflow: ScientificWorkflow):
        self._wrapped = workflow

    def _preprocess_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._wrapped._preprocess_data(input_data)
    def _perform_computation(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._wrapped._perform_computation(processed_data)


class LoggingDecorator(WorkflowDecorator):
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        print(f"🚀 开始执行工作流: {self._wrapped.__class__.__name__}")
        start = time.time()
        result = super().execute(input_data)
        elapsed = time.time() - start
        print(f"✅ 执行完成，耗时 {elapsed:.3f}s")
        return result


class CachingDecorator(WorkflowDecorator):
    def __init__(self, workflow: ScientificWorkflow, cache_dir: str = "./cache"):
        super().__init__(workflow)
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        cache_key = hashlib.md5(json.dumps(input_data, sort_keys=True).encode()).hexdigest()[:16]
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        if os.path.exists(cache_path):
            print(f"📦 从缓存加载结果")
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        result = super().execute(input_data)
        if 'error' not in result:
            with open(cache_path, 'wb') as f:
                pickle.dump(result, f)
            print(f"💾 结果已缓存")
        return result


# ---------- 抽象工厂模式：创建整套相关组件 ----------
class Validator(ABC):
    @abstractmethod
    def validate(self, data): pass

class Visualizer(ABC):
    @abstractmethod
    def visualize(self, result): pass


class NumericalValidator(Validator):
    def validate(self, data): print(" 数值验证器: 检查数值稳定性")

class NumericalVisualizer(Visualizer):
    def visualize(self, result): print(f" 数值可视化: 收敛率={result.get('convergence_rate')}")


class DataAnalysisValidator(Validator):
    def validate(self, data): print(" 分析验证器: 检查统计显著性")

class DataAnalysisVisualizer(Visualizer):
    def visualize(self, result): print(f" 分析可视化: 统计结果={result.get('statistics')}")


class WorkflowFactory(ABC):
    @abstractmethod
    def create_workflow(self) -> ScientificWorkflow:
        pass
    @abstractmethod
    def create_validator(self) -> Validator:
        pass
    @abstractmethod
    def create_visualizer(self) -> Visualizer:
        pass


class NumericalSimulationFactory(WorkflowFactory):
    def create_workflow(self) -> ScientificWorkflow:
        return NumericalSimulationWorkflow()
    def create_validator(self) -> Validator:
        return NumericalValidator()
    def create_visualizer(self) -> Visualizer:
        return NumericalVisualizer()


class DataAnalysisFactory(WorkflowFactory):
    def create_workflow(self) -> ScientificWorkflow:
        return DataAnalysisWorkflow()
    def create_validator(self) -> Validator:
        return DataAnalysisValidator()
    def create_visualizer(self) -> Visualizer:
        return DataAnalysisVisualizer()


# ==================== 高级数值工作流：集成策略模式 ====================

class AdvancedNumericalWorkflow(ScientificWorkflow):
    """将策略模式集成到模板方法中"""
    def __init__(self, default_algorithm: NumericalAlgorithm = None):
        super().__init__()
        self._algo_context = AlgorithmContext(default_algorithm)

    def set_algorithm(self, algorithm: NumericalAlgorithm):
        self._algo_context.set_algorithm(algorithm)

    def _preprocess_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        print("高级数值工作流预处理")
        problem_type = input_data.get('problem_type', 'general')
        if problem_type == 'structural':
            self.set_algorithm(FiniteElementMethod())
        elif problem_type == 'wave':
            self.set_algorithm(FiniteDifferenceMethod())
        elif problem_type == 'periodic':
            self.set_algorithm(SpectralMethod())
        else:
            self.set_algorithm(FiniteElementMethod())
        print(f" 自动选择算法: {self._algo_context._algorithm.get_info()['name']}")
        return input_data

    def _perform_computation(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        print("执行可插拔算法计算...")
        return self._algo_context.execute(processed_data)


# ==================== 人和（组件集成）：工厂 + 装饰器链组装 ====================

def build_enhanced_workflow(factory: WorkflowFactory,
                            enable_logging: bool = True,
                            enable_caching: bool = False) -> ScientificWorkflow:
    """人和：使用工厂创建组件，通过装饰器链增强，简化集成"""
    workflow = factory.create_workflow()
    if enable_logging:
        workflow = LoggingDecorator(workflow)
    if enable_caching:
        workflow = CachingDecorator(workflow)
    return workflow


# ==================== 演示入口 ====================

def demonstrate_scientific_workflow_engine():
    print("=" * 60)
    print("科学计算工作流引擎 - 基于三元框架的模式联奏演示")
    print("=" * 60)

    # 1. 地方：模板方法保证流程规范
    print("\n【地方】模板方法：数值模拟工作流骨架")
    basic_workflow = NumericalSimulationWorkflow()
    data = {'parameters': {'youngs_modulus': 200e9}, 'elements': 1500}
    result = basic_workflow.execute(data)
    print(f" 结果: {result}")

    # 2. 天圆：抽象工厂创建整套组件族
    print("\n【天圆】抽象工厂：创建数值模拟全家桶")
    factory = NumericalSimulationFactory()
    workflow = factory.create_workflow()
    validator = factory.create_validator()
    visualizer = factory.create_visualizer()
    print(" 工作流:", workflow.__class__.__name__)
    validator.validate(data)
    result2 = workflow.execute(data)
    visualizer.visualize(result2)

    # 3. 天圆：策略模式动态切换算法
    print("\n【天圆】策略模式：动态切换算法")
    adv_workflow = AdvancedNumericalWorkflow()
    for problem_type in ['structural', 'wave', 'periodic']:
        print(f"\n 问题类型: {problem_type}")
        res = adv_workflow.execute({'problem_type': problem_type, 'elements': 200})
        print(f" 算法结果: {res}")

    # 4. 天圆：装饰器动态增强
    print("\n【天圆】装饰器模式：动态增强工作流（日志+缓存）")
    enhanced = build_enhanced_workflow(NumericalSimulationFactory(),
                                       enable_logging=True, enable_caching=True)
    test_data = {'parameters': {'test': 1.0}, 'elements': 500}
    print("第一次执行:")
    enhanced.execute(test_data)
    print("第二次执行（应命中缓存）:")
    enhanced.execute(test_data)

    # 5. 人和：组件集成演示 - 不同工厂无缝切换
    print("\n【人和】组件集成：数据分析工作流")
    analysis_factory = DataAnalysisFactory()
    analysis_workflow = build_enhanced_workflow(analysis_factory, enable_logging=True)
    analysis_data = {'dataset': 'weather_2024', 'metrics': ['temp', 'humidity']}
    analysis_result = analysis_workflow.execute(analysis_data)
    print(f" 分析结果统计: {analysis_result.get('statistics')}")

    print("\n演示完成 - 三元框架和谐统一")


if __name__ == "__main__":
    demonstrate_scientific_workflow_engine()
