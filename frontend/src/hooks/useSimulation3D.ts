import { useState, useCallback } from "react";

export interface ICell3D {
    x: number;
    y: number;
    z: number;
    value: number;
}

export interface ISimulationParams3D {
    steps: number;
    alpha: number;
    runs: number; // Количество запусков для симуляции
}

const DEFAULT_PARAMS: ISimulationParams3D = {
    steps: 500,
    alpha: 0.5,
    runs: 1,
};

// API URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export const useSimulation3D = () => {
    const [cells, setCells] = useState<ICell3D[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [simulationParams, setSimulationParams] =
        useState<ISimulationParams3D>(DEFAULT_PARAMS);
    const [isSimulationCompleted, setIsSimulationCompleted] =
        useState<boolean>(false);
    const [limitShapeImage, setLimitShapeImage] = useState<string | null>(null);
    // Состояние для переключения между обычной визуализацией и предельной формой
    const [showLimitShape, setShowLimitShape] = useState(false);

    const startSimulation = useCallback(async (params: ISimulationParams3D) => {
        setIsLoading(true);
        setError(null);
        setSimulationParams(params);
        setIsSimulationCompleted(false);
        setLimitShapeImage(null);

        try {
            console.log("Starting 3D simulation with params:", params);

            // Симуляция на сервере - отправляем только поддерживаемые параметры
            const apiParams = {
                steps: params.steps,
                alpha: params.alpha,
                runs: params.runs || 1,
                // Убран параметр algorithm
            };

            console.log("Sending to API:", apiParams);

            const response = await fetch(`${API_BASE_URL}/simulate/3d`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(apiParams),
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(
                    `Ошибка при запуске симуляции: ${response.status} ${response.statusText}. ${errorText}`
                );
            }

            const simulationData = await response.json();
            console.log("Simulation data:", simulationData);

            if (simulationData.cells && Array.isArray(simulationData.cells)) {
                setCells(simulationData.cells);
                setIsSimulationCompleted(true);
            } else {
                // Если нет прямого ответа с ячейками, делаем дополнительный запрос на визуализацию
                const visualizationResponse = await fetch(
                    `${API_BASE_URL}/visualize/3d` // Обновлено: без параметра типа визуализации
                );
                if (!visualizationResponse.ok) {
                    const errorText = await visualizationResponse.text();
                    throw new Error(
                        `Ошибка при получении визуализации: ${visualizationResponse.status} ${visualizationResponse.statusText}. ${errorText}`
                    );
                }

                const visualizationData = await visualizationResponse.json();
                console.log("Visualization data:", visualizationData);

                if (
                    visualizationData.cells &&
                    Array.isArray(visualizationData.cells)
                ) {
                    setCells(visualizationData.cells);
                    setIsSimulationCompleted(true);
                } else {
                    throw new Error("Полученные данные имеют неверный формат");
                }
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : "Неизвестная ошибка");
            console.error("API Error:", err);
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Добавляем функцию для получения предельной формы
    const fetchLimitShape = useCallback(async () => {
        if (!isSimulationCompleted) {
            setError("Сначала необходимо выполнить симуляцию");
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            const response = await fetch(`${API_BASE_URL}/limit-shape/3d`);
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(
                    `Ошибка при получении предельной формы: ${response.status} ${response.statusText}. ${errorText}`
                );
            }

            const data = await response.json();
            if (data.image) {
                setLimitShapeImage(data.image);
            } else {
                throw new Error(
                    "Ошибка при получении изображения предельной формы"
                );
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : "Неизвестная ошибка");
            console.error("API Error:", err);
        } finally {
            setIsLoading(false);
        }
    }, [isSimulationCompleted]);

    // Обработчик для кнопки переключения режима отображения
    const handleToggleView = () => {
        if (!showLimitShape && !limitShapeImage && isSimulationCompleted) {
            fetchLimitShape();
        }
        setShowLimitShape(!showLimitShape);
    };
    return {
        cells,
        isLoading,
        showLimitShape,
        error,
        handleToggleView,
        simulationParams,
        startSimulation,
        isSimulationCompleted,
        limitShapeImage,
        fetchLimitShape,
    };
};
