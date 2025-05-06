import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from typing import Dict, Tuple, List, Any, Set, Union, Optional
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def save_cells_to_file(cell_counts: Dict[Tuple, int], filename: str) -> None:
    """
    Сохранение количества ячеек в текстовый файл.
    
    Параметры:
    -----------
    cell_counts : Dict[Tuple, int]
        Словарь с координатами ячеек в качестве ключей и количеством в качестве значений.
    filename : str
        Имя выходного файла.
    """
    try:
        with open(filename, 'w') as f:
            for coords, count in sorted(cell_counts.items()):
                # Обработка координат как для 2D, так и для 3D
                if len(coords) == 2:
                    x, y = coords
                    f.write(f'{x},{y},{count}\n')
                elif len(coords) == 3:
                    x, y, z = coords
                    f.write(f'{x},{y},{z},{count}\n')
        logger.info(f"Данные успешно сохранены в файл: {filename}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении в файл {filename}: {str(e)}")
        raise


def compute_limit_shape(cell_counts: Dict[Tuple, int], 
                        scaling_factor: Optional[float] = None,
                        dimensions: int = 2) -> Tuple:
    """
    Вычисление предельной формы на основе накопленных данных.
    
    Параметры:
    -----------
    cell_counts : Dict[Tuple, int]
        Словарь с координатами ячеек в качестве ключей и количеством в качестве значений.
    scaling_factor : float, optional
        Коэффициент масштабирования. Если None, используется sqrt(n) для 2D или cbrt(n) для 3D.
    dimensions : int
        Количество измерений (2 или 3).
        
    Возвращает:
    --------
    Кортеж координат сетки и интерполированных значений.
    
    Исключения:
    --------
    ValueError: Если нет данных для вычисления или указано неверное количество измерений.
    """
    if not cell_counts:
        raise ValueError("Нет данных для вычисления предельной формы")
    
    if dimensions not in [2, 3]:
        raise ValueError(f"Неподдерживаемое количество измерений: {dimensions}. Поддерживаются только 2D и 3D.")
    
    # Определение коэффициента масштабирования
    if scaling_factor is None:
        if dimensions == 2:
            n = max(x + y for x, y in cell_counts.keys())
            scaling_factor = np.sqrt(n)
        elif dimensions == 3:
            n = max(x + y + z for x, y, z in cell_counts.keys())
            scaling_factor = np.cbrt(n)
    
    # Проверка на положительность масштабного коэффициента
    if scaling_factor <= 0:
        raise ValueError(f"Коэффициент масштабирования должен быть положительным, получено: {scaling_factor}")
    
    # Масштабирование координат и нормализация частот
    scaled_points = []
    frequencies = []
    max_freq = max(cell_counts.values())
    
    for coords, count in cell_counts.items():
        scaled_coords = [c/scaling_factor for c in coords]
        scaled_points.append(scaled_coords)
        frequencies.append(count/max_freq)
    
    scaled_points = np.array(scaled_points)
    
    if dimensions == 2:
        # Создание регулярной сетки для интерполяции
        x_max = max(p[0] for p in scaled_points)
        y_max = max(p[1] for p in scaled_points)
        grid_x, grid_y = np.mgrid[0:x_max:100j, 0:y_max:100j]
        
        # Интерполяция данных
        grid_z = griddata(scaled_points, frequencies, (grid_x, grid_y), method='cubic', fill_value=0)
        
        return grid_x, grid_y, grid_z
    
    elif dimensions == 3:
        # Создание регулярной сетки для 3D интерполяции
        x_max = max(p[0] for p in scaled_points)
        y_max = max(p[1] for p in scaled_points)
        z_max = max(p[2] for p in scaled_points)
        grid_x, grid_y, grid_z = np.mgrid[0:x_max:50j, 0:y_max:50j, 0:z_max:50j]
        
        # Интерполяция данных
        grid_v = griddata(scaled_points, frequencies, (grid_x, grid_y, grid_z), method='linear', fill_value=0)
        
        return grid_x, grid_y, grid_z, grid_v
