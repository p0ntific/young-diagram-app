import React, { useState } from "react";
import FlexBox from "../ui-kit/FlexBox";

interface ISimulationFormProps {
    onSubmit: (params: any) => void;
    isLoading: boolean;
    defaultParams: {
        steps: number;
        alpha: number;
        runs: number;
    };
    isSimulationCompleted?: boolean;
    handleToggleView?: () => void;
    showLimitShape?: boolean;
}

const SimulationForm: React.FC<ISimulationFormProps> = ({
    onSubmit,
    isLoading,
    isSimulationCompleted,
    handleToggleView,
    showLimitShape,
    defaultParams,
}) => {
    const [steps, setSteps] = useState<string>("500");
    const [alpha, setAlpha] = useState<string>("0.5");
    const [runs, setRuns] = useState<string>("5");

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit({
            steps: steps === "" ? defaultParams.steps : Number(steps),
            alpha: alpha === "" ? defaultParams.alpha : Number(alpha),
            runs: runs === "" ? defaultParams.runs : Number(runs),
        });
    };

    return (
        <div className="visualization-container">
            <FlexBox direction="column" padding={24} gap={24}>
                <h2>Параметры симуляции</h2>

                <FlexBox direction="column" gap={16} style={{ width: "100%" }}>
                    <label>
                        <div style={{ marginBottom: "8px" }}>
                            Количество шагов (10-10000)
                        </div>
                        <input
                            type="number"
                            min={10}
                            max={10000}
                            value={steps}
                            onChange={(e) => setSteps(e.target.value)}
                            placeholder={defaultParams.steps.toString()}
                            required
                        />
                    </label>

                    <label>
                        <div style={{ marginBottom: "8px" }}>
                            Параметр α (-4.0 - 4.0)
                            <div
                                style={{
                                    fontSize: "0.8rem",
                                    color: "var(--text-muted)",
                                }}
                            >
                                Влияет на скорость роста диаграммы
                            </div>
                        </div>
                        <input
                            type="number"
                            min={-4}
                            max={4}
                            value={alpha}
                            onChange={(e) => setAlpha(e.target.value)}
                            placeholder={defaultParams.alpha.toString()}
                            required
                        />
                    </label>

                    <label>
                        <div style={{ marginBottom: "8px" }}>
                            Количество запусков (1-50)
                            <div
                                style={{
                                    fontSize: "0.8rem",
                                    color: "var(--text-muted)",
                                }}
                            >
                                Больше запусков - более точный результат
                            </div>
                        </div>
                        <input
                            type="number"
                            min={1}
                            max={50}
                            value={runs}
                            onChange={(e) => setRuns(e.target.value)}
                            placeholder={defaultParams.runs.toString()}
                            required
                        />
                    </label>
                </FlexBox>

                <button
                    type="submit"
                    className="primary"
                    onClick={handleSubmit}
                    disabled={isLoading}
                    style={{ position: "relative", width: "100%" }}
                >
                    {isLoading ? (
                        <>
                            <span style={{ opacity: 0.7 }}>Симуляция...</span>
                            <div className="button-loader"></div>
                        </>
                    ) : (
                        "Запустить симуляцию"
                    )}
                </button>
                {isSimulationCompleted && (
                    <button
                        onClick={handleToggleView}
                        style={{ width: "100%" }}
                    >
                        {showLimitShape
                            ? "Показать диаграмму"
                            : "Показать предельную форму"}
                    </button>
                )}
            </FlexBox>
        </div>
    );
};

export { SimulationForm };
