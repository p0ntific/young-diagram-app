import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from collections import defaultdict
from typing import Dict, Tuple, List, Set, Optional, Union, Any
import os
import sys
from matplotlib import cm
import matplotlib.colors as mcolors
import logging
import pickle

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.utils import save_cells_to_file, compute_limit_shape
from diagrams3d.young_diagram import Diagram3D

# Конфигурация визуализации
class VisualizationConfig:
    """
    Класс с настройками визуализации для 3D диаграмм.
    """
    DEFAULT_FIGURE_SIZE = (10, 10)
    DEFAULT_DPI = 300
    DEFAULT_COLORMAP = 'plasma'
    DEFAULT_ISOSURFACE_LEVEL = 0.5
    DEFAULT_ALPHA_CUBES = 0.7
    DEFAULT_ALPHA_SURFACE = 0.7
    DEFAULT_ELEV = 20
    DEFAULT_AZIM = -30
    DEFAULT_SLICE_COUNT = 3
    DEFAULT_POINT_SIZE_FACTOR = 100


class DiagramSimulator3D:
    """
    Класс для симуляции роста 3D диаграммы Юнга и записи результатов.
    """
    def __init__(self):
        """
        Инициализируем с пустым значением
        """
        self.total_cell_counts = defaultdict(int)  # словарь для подсчета количества дубликатов в каждой ячейке
        
    def simulate(self, n_steps: int = 1000, alpha: float = 1.0, runs: int = 10, 
                 initial_cells: Optional[Set[Tuple[int, int, int]]] = None, 
                 callback: Optional[callable] = None) -> None:
        """
        Выполняет симуляцию роста 3D диаграммы Юнга.

        Параметры:
        -----------
        n_steps : int, default=1000
            Количество шагов для каждой симуляции.
        alpha : float, default=1.0
            Степенной параметр для управления поведением роста.
        runs : int, default=10
            Количество симуляций для выполнения.
        initial_cells : Set[Tuple[int, int, int]], optional
            Начальный набор ячеек для симуляции.
        callback : callable, optional
            Функция, которая вызывается после каждого шага с текущим состоянием.

        Возвращает:
        -----------
        None
        
        Исключения:
        -----------
        ValueError: Если входные параметры некорректны.
        """
        # Валидация входных параметров
        if n_steps <= 0:
            raise ValueError("Количество шагов должно быть положительным числом")
        if runs <= 0:
            raise ValueError("Количество симуляций должно быть положительным числом")
            
        # Обновляем счетчик для новой симуляции
        self.total_cell_counts = defaultdict(int)
        
        for run in range(1, runs + 1):
            try:
                # Создаем новую диаграмму на каждый запуск
                diagram = Diagram3D(initial_cells)
                
                # Отслеживаем рост диаграммы в реальном времени
                def growth_callback(diagram, step):
                    if callback:
                        # Сохраняем текущее состояние для внешнего вызова
                        temp_counts = self.total_cell_counts.copy()
                        for cell in diagram.cells:
                            temp_counts[cell] += 1
                        callback(temp_counts, step, run)
                
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
                 alpha_cubes: float = VisualizationConfig.DEFAULT_ALPHA_CUBES,
                 elev: int = VisualizationConfig.DEFAULT_ELEV, 
                 azim: int = VisualizationConfig.DEFAULT_AZIM,
                 colormap: str = VisualizationConfig.DEFAULT_COLORMAP) -> plt.Figure:
        """
        Визуализирует результаты симуляции с помощью вокселей.
        
        Параметры:
        -----------
        filename : str, optional
            Имя файла для сохранения визуализации.
        alpha_cubes : float, default=0.7
            Прозрачность кубов.
        elev : int, default=20
            Угол возвышения для 3D вида.
        azim : int, default=-30
            Азимутальный угол для 3D вида.
        colormap : str, default='plasma'
            Цветовая карта для визуализации.
            
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
        
        try:    
            # Находим размеры 3D пространства
            max_x = max(x for x, _, _ in self.total_cell_counts.keys()) + 1
            max_y = max(y for _, y, _ in self.total_cell_counts.keys()) + 1
            max_z = max(z for _, _, z in self.total_cell_counts.keys()) + 1
            
            # Создаем булев массив для заполнения вокселей
            voxels = np.zeros((max_x, max_y, max_z), dtype=bool)
            
            # Создаем массив цветов для вокселей
            max_count = max(self.total_cell_counts.values())
            colors = np.zeros(voxels.shape + (4,))  # RGBA colors
            
            # Заполняем массивы вокселей и цветов
            for (x, y, z), count in self.total_cell_counts.items():
                voxels[x, y, z] = True
                
                # Нормализуем счетчик и создаем цвет
                normalized_count = count / max_count
                color_func = getattr(cm, colormap)
                colors[x, y, z] = color_func(normalized_count)
                # Последнее значение - это alpha (прозрачность)
                colors[x, y, z, 3] = alpha_cubes
            
            # Создаем фигуру
            fig = plt.figure(figsize=VisualizationConfig.DEFAULT_FIGURE_SIZE)
            ax = fig.add_subplot(111, projection='3d')
            
            # Рисуем воксели
            ax.voxels(voxels, facecolors=colors, edgecolor='k', linewidth=0.5)
            
            # Настраиваем подписи осей
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            
            # Устанавливаем угол обзора
            ax.view_init(elev=elev, azim=azim)
            
            # Корректируем соотношение сторон, чтобы кубы отображались как кубы, а не растянутые параллелепипеды
            max_dim = max(max_x, max_y, max_z)
            
            # Устанавливаем одинаковое соотношение сторон для всех осей
            ax.set_box_aspect([max_x/max_dim, max_y/max_dim, max_z/max_dim])
            
            # Устанавливаем одинаковый масштаб для всех осей
            ax.set_xlim(0, max_dim)
            ax.set_ylim(0, max_dim)
            ax.set_zlim(0, max_dim)
            
            ax.set_title('3D Диаграмма Юнга')
            
            # Добавляем цветовую шкалу
            norm = plt.Normalize(0, 1)
            sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
            sm.set_array([])
            plt.colorbar(sm, ax=ax, label='Нормализованная частота')
            
            # Сохраняем, если указано имя файла
            if filename:
                plt.savefig(filename, dpi=VisualizationConfig.DEFAULT_DPI, bbox_inches='tight')
                logger.info(f"Изображение сохранено: {filename}")
                
            plt.show()
            
            # Возвращаем фигуру для использования в веб-API
            return fig
            
        except Exception as e:
            logger.error(f"Ошибка при визуализации: {str(e)}")
            raise
    
    def visualize_point_cloud(self, filename: Optional[str] = None, 
                             alpha_points: float = 0.8, 
                             size_factor: int = VisualizationConfig.DEFAULT_POINT_SIZE_FACTOR,
                             colormap: str = VisualizationConfig.DEFAULT_COLORMAP) -> plt.Figure:
        """
        Визуализирует результаты симуляции в виде облака точек разных размеров.
        
        Параметры:
        -----------
        filename : str, optional
            Имя файла для сохранения визуализации.
        alpha_points : float, default=0.8
            Прозрачность точек.
        size_factor : int, default=100
            Коэффициент размера для точек.
        colormap : str, default='plasma'
            Цветовая карта для визуализации.
            
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
            
        try:
            # Извлекаем координаты и счетчики
            x_coords = []
            y_coords = []
            z_coords = []
            sizes = []
            colors = []
            
            max_count = max(self.total_cell_counts.values())
            
            for (x, y, z), count in self.total_cell_counts.items():
                x_coords.append(x)
                y_coords.append(y)
                z_coords.append(z)
                
                # Размер пропорционален счетчику
                normalized_count = count / max_count
                sizes.append(normalized_count * size_factor)
                colors.append(normalized_count)
            
            # Создаем фигуру
            fig = plt.figure(figsize=VisualizationConfig.DEFAULT_FIGURE_SIZE)
            ax = fig.add_subplot(111, projection='3d')
            
            # Создаем диаграмму рассеяния
            scatter = ax.scatter(x_coords, y_coords, z_coords, 
                               c=colors, cmap=colormap, s=sizes, alpha=alpha_points)
            
            # Добавляем цветовую шкалу
            plt.colorbar(scatter, ax=ax, label='Нормализованная частота')
            
            # Настраиваем подписи осей
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            
            # Находим максимальный размер в любом измерении
            max_dim = max(max(x_coords), max(y_coords), max(z_coords)) + 1
            
            # Устанавливаем одинаковое соотношение сторон для всех осей
            ax.set_box_aspect([1, 1, 1])
            
            # Устанавливаем одинаковые пределы для всех осей
            ax.set_xlim(0, max_dim)
            ax.set_ylim(0, max_dim)
            ax.set_zlim(0, max_dim)
            
            ax.set_title('Облако точек 3D диаграммы Юнга')
            
            # Сохраняем, если указано имя файла
            if filename:
                plt.savefig(filename, dpi=VisualizationConfig.DEFAULT_DPI, bbox_inches='tight')
                logger.info(f"Изображение облака точек сохранено: {filename}")
                
            plt.show()
            
            # Возвращаем фигуру для использования в веб-API
            return fig
            
        except Exception as e:
            logger.error(f"Ошибка при визуализации облака точек: {str(e)}")
            raise
    
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
        
    def visualize_limit_shape(self, filename: Optional[str] = None, 
                             level: float = VisualizationConfig.DEFAULT_ISOSURFACE_LEVEL, 
                             alpha_surface: float = VisualizationConfig.DEFAULT_ALPHA_SURFACE,
                             colormap: str = VisualizationConfig.DEFAULT_COLORMAP) -> plt.Figure:
        """
        Визуализирует предельную форму с помощью изоповерхностей в 3D.
        
        Параметры:
        -----------
        filename : str, optional
            Имя файла для сохранения визуализации.
        level : float, default=0.5
            Уровень изоповерхности для отображения (от 0 до 1).
        alpha_surface : float, default=0.7
            Прозрачность поверхности.
        colormap : str, default='viridis'
            Цветовая карта для визуализации.
            
        Возвращает:
        -----------
        plt.Figure
            Объект фигуры matplotlib для дальнейшей настройки или отображения.
            
        Исключения:
        -----------
        ValueError: Если нет клеток для отображения или не установлена библиотека skimage.
        """
        if not self.total_cell_counts:
            raise ValueError("Нет клеток, которые можно отобразить. Запустите симуляцию перед визуализацией.")
            
        try:
            # Эта функция требует skimage
            from skimage import measure
        except ImportError:
            logger.error("Для этой визуализации требуется scikit-image. Установите его с помощью:")
            logger.error("pip install scikit-image")
            raise ValueError("Требуется библиотека scikit-image")
            
        try:
            # Вычисляем предельную форму
            grid_x, grid_y, grid_z, grid_v = compute_limit_shape(
                self.total_cell_counts, dimensions=3)
            
            # Извлекаем изоповерхность на указанном уровне
            verts, faces, _, _ = measure.marching_cubes(grid_v, level=level)
            
            # Масштабируем вершины обратно к исходной системе координат
            x_size, y_size, z_size = grid_x.max(), grid_y.max(), grid_z.max()
            verts[:, 0] *= x_size / grid_v.shape[0]
            verts[:, 1] *= y_size / grid_v.shape[1] 
            verts[:, 2] *= z_size / grid_v.shape[2]
            
            # Создаем фигуру
            fig = plt.figure(figsize=VisualizationConfig.DEFAULT_FIGURE_SIZE)
            ax = fig.add_subplot(111, projection='3d')
            
            # Рисуем изоповерхность
            mesh = ax.plot_trisurf(verts[:, 0], verts[:, 1], verts[:, 2],
                                  triangles=faces, cmap=colormap, alpha=alpha_surface)
            
            # Настраиваем подписи осей
            ax.set_xlabel('x/n^(1/3)')
            ax.set_ylabel('y/n^(1/3)')
            ax.set_zlabel('z/n^(1/3)')
            
            # Устанавливаем одинаковое соотношение сторон
            ax.set_box_aspect([1, 1, 1])
            
            ax.set_title(f'Предельная форма 3D диаграммы Юнга (Изоповерхность на уровне {level})')
            
            # Сохраняем, если указано имя файла
            if filename:
                plt.savefig(filename, dpi=VisualizationConfig.DEFAULT_DPI, bbox_inches='tight')
                logger.info(f"Изображение предельной формы сохранено: {filename}")
                
            plt.show()
            
            # Возвращаем фигуру для использования в веб-API
            return fig
            
        except Exception as e:
            logger.error(f"Ошибка при визуализации предельной формы: {str(e)}")
            raise
        
    def visualize_slices(self, filename: Optional[str] = None, 
                        num_slices: int = VisualizationConfig.DEFAULT_SLICE_COUNT,
                        colormap: str = VisualizationConfig.DEFAULT_COLORMAP) -> plt.Figure:
        """
        Визуализирует 2D срезы 3D диаграммы на разных уровнях z.
        
        Параметры:
        -----------
        filename : str, optional
            Имя файла для сохранения визуализации.
        num_slices : int, default=3
            Количество z-срезов для отображения.
        colormap : str, default='plasma'
            Цветовая карта для визуализации.
            
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
        
        try:    
            # Находим диапазон значений z
            z_values = [z for _, _, z in self.total_cell_counts.keys()]
            min_z, max_z = min(z_values), max(z_values)
            
            # Определяем позиции срезов
            if num_slices == 1:
                slice_positions = [min_z]
            else:
                slice_positions = np.linspace(min_z, max_z, num_slices, dtype=int)
            
            # Создаем фигуру с подграфиками
            fig, axes = plt.subplots(1, len(slice_positions), figsize=(15, 5))
            if num_slices == 1:
                axes = [axes]
                
            # Устанавливаем заголовок для всей фигуры
            fig.suptitle('Срезы 3D диаграммы Юнга по Z', fontsize=16)
            
            # Максимальное значение счетчика для нормализации
            max_count = max(self.total_cell_counts.values())
            
            # Обрабатываем каждый срез
            for i, z in enumerate(slice_positions):
                # Извлекаем ячейки на этом уровне z
                slice_cells = {(x, y): count for (x, y, z_val), count in self.total_cell_counts.items() if z_val == z}
                
                if not slice_cells:
                    axes[i].text(0.5, 0.5, f'Нет ячеек при z={z}', 
                               horizontalalignment='center', verticalalignment='center')
                    axes[i].set_title(f'z = {z}')
                    continue
                    
                # Подготавливаем данные для визуализации
                x_coords, y_coords, frequencies = [], [], []
                for (x, y), count in slice_cells.items():
                    x_coords.append(x)
                    y_coords.append(y)
                    frequencies.append(count / max_count)
                    
                # Создаем диаграмму рассеяния для этого среза
                scatter = axes[i].scatter(x_coords, y_coords, c=frequencies, cmap=colormap, 
                                       s=100, alpha=0.8, edgecolors='k', marker='s')
                
                axes[i].set_title(f'z = {z}')
                axes[i].set_xlabel('x')
                axes[i].set_ylabel('y')
                axes[i].grid(True)
                axes[i].set_aspect('equal')
                
            # Добавляем общую цветовую шкалу
            plt.colorbar(scatter, ax=axes, label='Нормализованная частота')
            
            plt.tight_layout(rect=[0, 0, 1, 0.95])  # Регулируем расположение, чтобы оставить место для заголовка
            
            # Сохраняем, если указано имя файла
            if filename:
                plt.savefig(filename, dpi=VisualizationConfig.DEFAULT_DPI, bbox_inches='tight')
                logger.info(f"Изображение срезов сохранено: {filename}")
                
            plt.show()
            
            # Возвращаем фигуру для использования в веб-API
            return fig
            
        except Exception as e:
            logger.error(f"Ошибка при визуализации срезов: {str(e)}")
            raise
        
    def get_json_data(self) -> Dict:
        """
        Получает данные в JSON-сериализуемом формате для веб-API.
        
        Возвращает:
        --------
        dict
            Словарь, содержащий данные о клетках для визуализации.
            
        Исключения:
        -----------
        ValueError: Если нет данных для экспорта.
        """
        if not self.total_cell_counts:
            return {"error": "Нет доступных данных. Сначала выполните симуляцию."}
            
        # Конвертируем в формат, подходящий для сериализации JSON
        cells_data = []
        max_count = max(self.total_cell_counts.values())
        
        for (x, y, z), count in self.total_cell_counts.items():
            normalized_count = count / max_count
            cells_data.append({
                "x": x,
                "y": y,
                "z": z,
                "count": count,
                "normalized_count": normalized_count
            })
            
        return {
            "cells": cells_data,
            "max_count": max_count,
            "dimensions": {
                "max_x": max(x for x, _, _ in self.total_cell_counts.keys()) + 1,
                "max_y": max(y for _, y, _ in self.total_cell_counts.keys()) + 1,
                "max_z": max(z for _, _, z in self.total_cell_counts.keys()) + 1
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
