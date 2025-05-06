import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from typing import Dict, Tuple, List, Set, Optional, Union, Any
import os
import sys
import pickle
import logging

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.utils import save_cells_to_file, compute_limit_shape
from diagrams2d.young_diagram import Diagram2D

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Конфигурация визуализации
class VisualizationConfig:
    """
    Класс с настройками визуализации для диаграмм.
    """
    DEFAULT_CELL_SIZE = 10
    DEFAULT_COLORMAP_HEATMAP = 'Reds_r'
    DEFAULT_COLORMAP_DENSITY = 'viridis'
    DEFAULT_FIGURE_SIZE = (10, 10)
    DEFAULT_CONTOUR_LEVELS = 10
    DEFAULT_DPI = 300
    DEFAULT_GRID = True


class DiagramSimulator2D:
    """
    Класс для симуляции роста диаграммы 2D и записи результатов в файл.
    """
    def __init__(self):
        """
        Инициализируем с пустым значением
        """
        self.total_cell_counts = defaultdict(int)  # словарь для подсчета количества дубликатов в каждой ячейке
        
    def simulate(self, n_steps: int = 1000, alpha: float = 1.0, runs: int = 10, 
                 initial_cells: Optional[Set[Tuple[int, int]]] = None,
                 callback: Optional[callable] = None) -> None:
        """
        Выполняет симуляцию роста диаграммы 2D.

        Параметры:
        -----------
        n_steps : int, default=1000
            Количество шагов для каждой симуляции.
        alpha : float, default=1.0
            Степенной параметр для управления поведением роста.
        runs : int, default=10
            Количество симуляций для выполнения.
        initial_cells : Set[Tuple[int, int]], optional
            Начальный набор ячеек для симуляции.
        callback : callable, optional
            Функция, которая вызывается после каждого шага с текущим состоянием.

        Возвращает:
        -----------
        None
        
        Исключения:
        --------
        ValueError: Если входные параметры некорректны.
        """
        # Валидация входных параметров
        if n_steps <= 0:
            raise ValueError("Количество шагов должно быть положительным числом")
        if runs <= 0:
            raise ValueError("Количество симуляций должно быть положительным числом")
        if alpha <= 0:
            raise ValueError("Параметр alpha должен быть положительным числом")
        
        # Обновляем счетчик для новой симуляции
        self.total_cell_counts = defaultdict(int)
        
        for run in range(1, runs + 1):
            # Создаем новую диаграмму на каждый запуск
            diagram = Diagram2D(initial_cells)
            
            # Отслеживаем рост диаграммы в реальном времени
            def growth_callback(diagram, step):
                if callback:
                    # Сохраняем текущее состояние для внешнего вызова
                    temp_counts = self.total_cell_counts.copy()
                    for cell in diagram.cells:
                        temp_counts[cell] += 1
                    callback(temp_counts, step, run)
            
            try:
                # Запускаем симуляцию
                diagram.simulate(n_steps=n_steps, alpha=alpha, callback=growth_callback)
                
                # Обновляем счетчик для каждой ячейки в диаграмме
                for cell in diagram.cells:
                    self.total_cell_counts[cell] += 1
                    
                logger.info(f'Симуляция {run} завершена. Размер диаграммы: {len(diagram.cells)} клеток.')
            except Exception as e:
                logger.error(f"Ошибка в симуляции {run}: {str(e)}")
                raise
    
    def visualize(self, filename: Optional[str] = None, 
              cell_size: int = VisualizationConfig.DEFAULT_CELL_SIZE, 
              grid: bool = VisualizationConfig.DEFAULT_GRID,
              min_color_value: float = 0.5) -> plt.Figure:
        """
        Визуализирует результаты симуляции.

        Параметры:
        -----------
        filename : str, optional
            Имя файла для сохранения визуализации.
        cell_size : int, default=10
            Размер ячейки в пикселях.
        grid : bool, default=True
            Отображать ли сетку.
        min_color_value : float, default=0.5
            Минимальная интенсивность цвета (от 0 до 1) для наименее частых ячеек.
            
        Возвращает:
        -----------
        plt.Figure
            Объект фигуры matplotlib для дальнейшей настройки или отображения.
            
        Исключения:
        -----------
        ValueError: Если нет клеток для отображения.
        """
        if not self.total_cell_counts:
            raise ValueError("Нет клеток, которые можно отобразить. Запустите симуляцию перед визуализацией.")
            
        # Определяем максимальные координаты для построения сетки
        max_x = max(x for x, _ in self.total_cell_counts.keys()) + 1
        max_y = max(y for _, y in self.total_cell_counts.keys()) + 1

        # Создаем сетку значений для улучшенного отображения
        grid_data = np.zeros((max_x, max_y))
        max_count = max(self.total_cell_counts.values())

        # Заполняем сетку нормализованными частотами
        for (x, y), count in self.total_cell_counts.items():
            normalized_count = count / max_count
            # Применяем масштабирование, чтобы малые вероятности были лучше видны
            adjusted_value = min_color_value + (1.0 - min_color_value) * normalized_count
            grid_data[x, y] = adjusted_value  # Не инвертируем значения

        # Создаем фигуру с белым/серым фоном
        plt.figure(figsize=VisualizationConfig.DEFAULT_FIGURE_SIZE, facecolor='white')
        ax = plt.gca()
        ax.set_facecolor('#f0f0f0')  # Светло-серый фон для графика

        # Создаем пользовательскую цветовую карту - от светло-серого к красному
        from matplotlib.colors import LinearSegmentedColormap
        # Градиент: серый (фон) -> белый -> светло-красный -> красный
        colors = [(0.94, 0.94, 0.94, 0), (1, 1, 1, 0.2), (1, 0.8, 0.8, 0.6), (0.8, 0, 0, 1)]
        custom_cmap = LinearSegmentedColormap.from_list('grey_to_red', colors, N=256)

        # Маскируем нулевые значения для прозрачности
        masked_data = np.ma.masked_where(grid_data == 0, grid_data)

        # Используем pcolormesh для более качественного отображения
        mesh = plt.pcolormesh(np.arange(max_x + 1) * cell_size / max_x, 
                                np.arange(max_y + 1) * cell_size / max_y,
                                masked_data.T,  # Транспонируем для правильной ориентации
                                cmap=custom_cmap,
                                edgecolors='none', 
                                shading='flat')

        plt.colorbar(mesh, label='Частота появления ячейки')
        plt.gca().set_aspect('equal', adjustable='box')

        # Настраиваем оси
        xticks = np.linspace(0, cell_size, min(11, max_x + 1))
        yticks = np.linspace(0, cell_size, min(11, max_y + 1))
        plt.xticks(xticks)
        plt.yticks(yticks)

        plt.xlabel('x')
        plt.ylabel('y')
        plt.title('Накопленная диаграмма Юнга (2D)')

        if grid:
            plt.grid(True, linestyle='-', linewidth=0.5, alpha=0.3, color='#cccccc')
            
        if filename:
            try:
                plt.savefig(filename, dpi=VisualizationConfig.DEFAULT_DPI, 
                            bbox_inches='tight', facecolor='white')
                logger.info(f"Изображение сохранено: {filename}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении изображения {filename}: {str(e)}")
                raise
            
        plt.show()

        return plt.gcf()

    
    def save_cells(self, filename: str) -> None:
        """
        Сохраняет все ячейки в файл.
        
        Параметры:
        -----------
        filename : str
            Имя файла для сохранения ячеек.
            
        Исключения:
        -----------
        Exception: При ошибке сохранения данных.
        """
        try:
            save_cells_to_file(self.total_cell_counts, filename)
            logger.info(f"Данные ячеек сохранены в файл: {filename}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных в {filename}: {str(e)}")
            raise

    def limit_shape_visualize(self, filename: Optional[str] = None, 
                             levels: int = VisualizationConfig.DEFAULT_CONTOUR_LEVELS) -> plt.Figure:
        """
        Визуализирует результаты симуляции в виде предельной формы.
        
        Параметры:
        -----------
        filename : str, optional
            Имя файла для сохранения визуализации.
        levels : int, default=10
            Количество уровней для контура.
            
        Возвращает:
        -----------
        plt.Figure
            Объект фигуры matplotlib.
            
        Исключения:
        -----------
        ValueError: Если нет клеток для отображения.
        """
        if not self.total_cell_counts:
            raise ValueError("Нет клеток, которые можно отобразить. Запустите симуляцию перед визуализацией.")
            
        try:
            # Вычисляем предельную форму
            grid_x, grid_y, grid_z = compute_limit_shape(
                self.total_cell_counts, dimensions=2)
            
            plt.figure(figsize=VisualizationConfig.DEFAULT_FIGURE_SIZE)
            
            # Plot contour graph
            contour = plt.contour(grid_x, grid_y, grid_z, levels=levels)
            plt.clabel(contour, inline=True, fontsize=8)
            
            # Add heatmap
            plt.imshow(grid_z.T, extent=[0, grid_x.max(), 0, grid_y.max()],
                      origin='lower', cmap=VisualizationConfig.DEFAULT_COLORMAP_DENSITY, alpha=0.5)
            
            plt.colorbar(label='Нормализованная частота')
            plt.xlabel('x/√n')
            plt.ylabel('y/√n')
            plt.title('Предельная форма диаграммы Юнга 2D')
            plt.axis('equal')
            plt.grid(True)
            
            if filename:
                plt.savefig(filename, dpi=VisualizationConfig.DEFAULT_DPI, bbox_inches='tight')
                logger.info(f"Изображение предельной формы сохранено: {filename}")
                
            plt.show()
            
            # Return the figure for web API usage
            return plt.gcf()
        
        except Exception as e:
            logger.error(f"Ошибка при визуализации предельной формы: {str(e)}")
            raise
        
    def get_json_data(self) -> Dict:
        """
        Получаем дату в удобном формате для API.
        
        Возвращает:
        -----------
        Dict
            Данные диаграммы в формате JSON.
        """
        if not self.total_cell_counts:
            return {"error": "Нет доступных данных. Сначала выполните симуляцию."}
            
        cells_data = []
        max_count = max(self.total_cell_counts.values())
        
        for (x, y), count in self.total_cell_counts.items():
            normalized_count = count / max_count
            cells_data.append({
                "x": x,
                "y": y,
                "count": count,
                "normalized_count": normalized_count
            })
            
        return {
            "cells": cells_data,
            "max_count": max_count,
            "dimensions": {
                "max_x": max(x for x, _ in self.total_cell_counts.keys()) + 1,
                "max_y": max(y for _, y in self.total_cell_counts.keys()) + 1
            }
        }
        
    def save_state(self, filename: str) -> None:
        """
        Сохраняет текущее состояние симуляции для возможности продолжения.
        
        Параметры:
        -----------
        filename : str
            Имя файла для сохранения состояния.
            
        Исключения:
        -----------
        Exception: При ошибке сохранения состояния.
        """
        state = {
            "total_cell_counts": dict(self.total_cell_counts)
        }
        try:
            with open(filename, 'wb') as f:
                pickle.dump(state, f)
            logger.info(f"Состояние симуляции сохранено в файл: {filename}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении состояния в {filename}: {str(e)}")
            raise
   
    def load_state(self, filename: str) -> None:
        """
        Загружает сохраненное состояние симуляции.
        
        Параметры:
        -----------
        filename : str
            Имя файла с сохраненным состоянием.
            
        Исключения:
        -----------
        Exception: При ошибке загрузки состояния.
        FileNotFoundError: Если файл не найден.
        """
        try:
            with open(filename, 'rb') as f:
                state = pickle.load(f)
                self.total_cell_counts = defaultdict(int, state["total_cell_counts"])
            logger.info(f"Состояние симуляции загружено из файла: {filename}")
        except FileNotFoundError:
            logger.error(f"Файл {filename} не найден")
            raise
        except Exception as e:
            logger.error(f"Ошибка при загрузке состояния из {filename}: {str(e)}")
            raise