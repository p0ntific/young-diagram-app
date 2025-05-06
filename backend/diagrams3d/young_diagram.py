import random
from typing import Set, Tuple, List, Dict, Optional, Union, Any
import logging

logger = logging.getLogger(__name__)

class Diagram3D:
    """
    Класс, представляющий 3D диаграмму Юнга с возможностями симуляции роста.
    
    3D диаграмма Юнга представляет собой коллекцию кубических ячеек с целочисленными координатами.
    Диаграмма следует правилу: если куб с координатами (x,y,z) находится в диаграмме,
    то все кубы с координатами (x',y',z'), где x' <= x, y' <= y, z' <= z, также должны быть в диаграмме.
    """
    def __init__(self, initial_cells: Optional[Set[Tuple[int, int, int]]] = None):
        """
        Инициализация 3D диаграммы Юнга.
        
        Параметры:
        -----------
        initial_cells : Set[Tuple[int, int, int]], optional
            Начальный набор ячеек. Если None, начинается с ячейки (0, 0, 0).
        """
        self.cells: Set[Tuple[int, int, int]] = initial_cells if initial_cells else {(0, 0, 0)}
        # Для оптимизации будем отслеживать граничные ячейки
        self._boundary_cells: Set[Tuple[int, int, int]] = self._calculate_boundary_cells()
        
    def _calculate_boundary_cells(self) -> Set[Tuple[int, int, int]]:
        """
        Определяет граничные ячейки диаграммы, которые могут иметь новые добавляемые соседи.
        
        Возвращает:
        --------
        Set[Tuple[int, int, int]]
            Множество граничных ячеек.
        """
        boundary = set()
        for x, y, z in self.cells:
            # Ячейки, которые находятся на границе в одном из трех положительных направлений
            if ((x + 1, y, z) not in self.cells or 
                (x, y + 1, z) not in self.cells or 
                (x, y, z + 1) not in self.cells):
                boundary.add((x, y, z))
        return boundary
        
    def get_addable_cells(self) -> Set[Tuple[int, int, int]]:
        """
        Находит все ячейки, которые можно добавить к диаграмме согласно правилам 3D диаграммы Юнга.
        Ячейка может быть добавлена, если у неё есть соседи во всех трех направлениях: слева, снизу и сзади.
        
        Возвращает:
        --------
        Set[Tuple[int, int, int]]
            Набор координат (x, y, z), которые можно добавить к диаграмме.
        """
        addable_cells = set()
        # Используем только граничные ячейки для оптимизации
        for x, y, z in self._boundary_cells:
            # Возможные новые ячейки в трех положительных направлениях
            neighbors = [(x + 1, y, z), (x, y + 1, z), (x, y, z + 1)]
            for nx, ny, nz in neighbors:
                # Если соседняя ячейка еще не в диаграмме
                if (nx, ny, nz) not in self.cells:
                    # Проверяем, есть ли у неё поддержка со всех трех сторон
                    has_support_below = ny == 0 or (nx, ny - 1, nz) in self.cells
                    has_left_neighbor = nx == 0 or (nx - 1, ny, nz) in self.cells
                    has_back_neighbor = nz == 0 or (nx, ny, nz - 1) in self.cells
                    
                    if has_support_below and has_left_neighbor and has_back_neighbor:
                        addable_cells.add((nx, ny, nz))
        return addable_cells
    
    def calculate_weight(self, cell: Tuple[int, int, int], alpha: float = 1.0) -> float:
        """
        Вычисляет вес ячейки для вероятностного выбора при росте диаграммы.
        
        Формула: S(c) = ((x + 1) * (y + 1) * (z + 1)) ** alpha, где:
        - x, y, z - координаты ячейки
        - alpha - параметр, влияющий на характер роста:
          * при alpha > 1: увеличивается вероятность роста вдоль диагонали
          * при alpha < 1: увеличивается вероятность равномерного роста
        
        Параметры:
        -----------
        cell : Tuple[int, int, int]
            Координаты ячейки (x, y, z).
        alpha : float, default=1.0
            Степенной параметр для управления поведением роста.
            
        Возвращает:
        --------
        float
            Вес ячейки для вероятностного выбора.
        """
        x, y, z = cell
        # Вычисляем объем прямоугольного параллелепипеда
        volume = (x + 1) * (y + 1) * (z + 1)
        return volume ** alpha
    
    def add_cell(self, cell: Tuple[int, int, int]) -> None:
        """
        Добавляет новую ячейку к диаграмме и обновляет граничные ячейки.
        
        Параметры:
        -----------
        cell : Tuple[int, int, int]
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
        if alpha <= 0:
            raise ValueError("Параметр alpha должен быть положительным числом")
            
        for step in range(n_steps):
            # Получаем все ячейки, которые можно добавить
            addable_cells = self.get_addable_cells()
            if not addable_cells:
                # Более информативное сообщение об ошибке
                logger.warning(f"На шаге {step} нет доступных клеток для добавления. Диаграмма достигла предела роста.")
                break
                
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
            
            # Вызываем callback, если он предоставлен и если сейчас подходящий шаг
            # Вызываем не на каждом шаге для оптимизации производительности
            if callback and step % 10 == 0:
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
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Собирает статистику о текущем состоянии диаграммы.
        
        Возвращает:
        --------
        Dict[str, Any]
            Словарь со статистическими данными о диаграмме:
            - size: количество ячеек
            - boundary_size: количество граничных ячеек
            - max_coords: максимальные координаты по каждой оси
            - volume: объем диаграммы (произведение максимальных координат + 1)
        """
        if not self.cells:
            return {
                "size": 0,
                "boundary_size": 0,
                "max_coords": (0, 0, 0),
                "volume": 0
            }
        
        max_x = max(x for x, _, _ in self.cells)
        max_y = max(y for _, y, _ in self.cells)
        max_z = max(z for _, _, z in self.cells)
        
        volume = (max_x + 1) * (max_y + 1) * (max_z + 1)
        
        return {
            "size": len(self.cells),
            "boundary_size": len(self._boundary_cells),
            "max_coords": (max_x, max_y, max_z),
            "volume": volume
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Сериализует диаграмму в словарь для сохранения.
        
        Возвращает:
        --------
        Dict[str, Any]
            Словарь с данными диаграммы.
        """
        return {
            "cells": list(self.cells),
            "boundary_cells": list(self._boundary_cells),
            "statistics": self.get_statistics()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Diagram3D':
        """
        Создает диаграмму из словаря (десериализация).
        
        Параметры:
        -----------
        data : Dict[str, Any]
            Словарь с данными диаграммы.
            
        Возвращает:
        --------
        Diagram3D
            Новый экземпляр диаграммы.
        """
        diagram = cls(set(tuple(cell) for cell in data["cells"]))
        # Отслеживание граничных ячеек будет автоматически обновлено при инициализации
        return diagram
