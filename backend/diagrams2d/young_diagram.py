import random
from typing import Set, Tuple, List, Dict, Optional, Union
import logging

logger = logging.getLogger(__name__)

class Diagram2D:
    """
    Класс, представляющий 2D диаграмму Юнга с возможностями симуляции роста.
    """
    def __init__(self, initial_cells: Optional[Set[Tuple[int, int]]] = None):
        """
        Инициализация 2D диаграммы Юнга.
        
        Параметры:
        -----------
        initial_cells : Set[Tuple[int, int]], optional
            Начальный набор ячеек. Если None, начинается с ячейки (0, 0).
        """
        self.cells: Set[Tuple[int, int]] = initial_cells if initial_cells else {(0, 0)}
        # Для оптимизации будем отслеживать граничные ячейки
        self._boundary_cells: Set[Tuple[int, int]] = self._calculate_boundary_cells()
        
    def _calculate_boundary_cells(self) -> Set[Tuple[int, int]]:
        """
        Определяет граничные ячейки диаграммы, которые могут иметь новые добавляемые соседи.
        
        Возвращает:
        --------
        Set[Tuple[int, int]]
            Множество граничных ячеек.
        """
        boundary = set()
        for x, y in self.cells:
            # Ячейки, которые находятся на правой или верхней границе
            if (x + 1, y) not in self.cells or (x, y + 1) not in self.cells:
                boundary.add((x, y))
        return boundary
    
    def get_addable_cells(self) -> Set[Tuple[int, int]]:
        """
        Находит все ячейки, которые можно добавить к диаграмме согласно правилам диаграммы Юнга.
        Ячейка может быть добавлена, если у неё есть соседи слева и снизу.
        
        Возвращает:
        --------
        Set[Tuple[int, int]]
            Набор координат (x, y), которые можно добавить к диаграмме.
        """
        addable_cells = set()
        # Используем только граничные ячейки для оптимизации
        for x, y in self._boundary_cells:
            # Возможные новые ячейки справа и сверху
            neighbors = [(x + 1, y), (x, y + 1)]
            for nx, ny in neighbors:
                # Если соседняя ячейка еще не в диаграмме
                if (nx, ny) in self.cells:
                    continue

                # Проверяем, есть ли у неё поддержка снизу и слева
                has_support_below = ny == 0 or (nx, ny - 1) in self.cells
                has_left_neighbor = nx == 0 or (nx - 1, ny) in self.cells
                if has_support_below and has_left_neighbor:
                    addable_cells.add((nx, ny))
                    
        return addable_cells
    
    def calculate_weight(self, cell: Tuple[int, int], alpha: float = 1.0) -> float:
        """
        Вычисляет вес ячейки для вероятностного выбора при росте диаграммы.
        
        Формула: S(c) = (x + y + 2) ** alpha, где:
        - x, y - координаты ячейки
        - alpha - параметр, влияющий на характер роста:
          * при alpha > 1: увеличивается вероятность роста вдоль диагонали
          * при alpha < 1: увеличивается вероятность равномерного роста
        
        Параметры:
        -----------
        cell : Tuple[int, int]
            Координаты ячейки (x, y).
        alpha : float, default=1.0
            Степенной параметр для управления поведением роста.
            
        Возвращает:
        --------
        float
            Вес ячейки для вероятностного выбора.
        """
        x, y = cell
        total = (x + 1) + (y + 1)  # Площадь прямоугольника
        return total ** alpha
    
    def add_cell(self, cell: Tuple[int, int]) -> None:
        """
        Добавляет новую ячейку к диаграмме и обновляет граничные ячейки.
        
        Параметры:
        -----------
        cell : Tuple[int, int]
            Координаты ячейки для добавления.
        """
        self.cells.add(cell)
        # Обновляем граничные ячейки
        self._boundary_cells = self._calculate_boundary_cells()
        
    def simulate(self, n_steps: int = 1000, alpha: float = 1.0, 
                 callback: Optional[callable] = None) -> None:
        """
        Симулирует рост диаграммы в течение n_steps итераций.
        
        Параметры:
        -----------
        n_steps : int, default=1000
            Количество шагов для симуляции.
        alpha : float, default=1.0
            Параметр, влияющий на поведение роста.
        callback : callable, optional
            Функция, которая вызывается после каждого шага с текущим состоянием.
            
        Исключения:
        --------
        ValueError: Если входные параметры некорректны или нет доступных ячеек для добавления.
        """
        # Валидация входных параметров
        if n_steps <= 0:
            raise ValueError("Количество шагов должно быть положительным числом")
            
        for step in range(n_steps):
            # Получаем все ячейки, которые можно добавить
            addable_cells = self.get_addable_cells()
            if not addable_cells:
                # Более информативное сообщение об ошибке
                raise ValueError(f"На шаге {step} нет доступных клеток для добавления. Диаграмма достигла предела роста.")
                
            # Вычисляем веса для каждой добавляемой ячейки
            weights = []
            cells_list = list(addable_cells)
            
            # Вычисляем S(c) для каждой добавляемой ячейки
            for cell in cells_list:
                weights.append(self.calculate_weight(cell, alpha))
                
            # Вычисляем вероятности для каждой ячейки
            total_weight = sum(weights)
            probabilities = [w / total_weight for w in weights]
            
            # Случайно выбираем ячейку для добавления на основе вероятностей
            cell = random.choices(cells_list, weights=probabilities, k=1)[0]
            self.add_cell(cell)
            
            # Вызываем callback, если он предоставлен
            if callback: 
                callback(self, step)
                
    def size(self) -> int:
        """
        Получает количество ячеек в диаграмме.
    
        Возвращает:
        --------
        int
            Количество ячеек в диаграмме.
        """
        return len(self.cells) 