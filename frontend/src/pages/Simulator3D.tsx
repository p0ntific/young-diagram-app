import React from "react";
import FlexBox from "../ui-kit/FlexBox";
import { SimulationForm } from "../components/SimulationForm";
import { VisualizationCanvas3D } from "../components/VisualizationCanvas3D";
import { useSimulation3D } from "../hooks/useSimulation3D";
import Header from "../components/Header";

const Simulator3D: React.FC = () => {
    const {
        cells,
        isLoading,
        error,
        simulationParams,
        startSimulation,
        showLimitShape,
        isSimulationCompleted,
        limitShapeImage,
        handleToggleView,
    } = useSimulation3D();

    return (
        <FlexBox direction="column" style={{ minHeight: "100vh" }}>
            <Header />
            <FlexBox
                direction="column"
                padding={40}
                gap={40}
                align="center"
                style={{
                    maxWidth: "1200px",
                    margin: "0 auto",
                    width: "100%",
                }}
            >
                <section style={{ width: "100%", textAlign: "center" }}>
                    <h1>3D Симулятор диаграмм Юнга</h1>
                    <p
                        className="text-muted"
                        style={{
                            margin: "0 auto",
                        }}
                    >
                        Настройте параметры и запустите симуляцию для
                        визуализации трехмерных диаграмм Юнга
                    </p>
                </section>
                <FlexBox
                    gap={24}
                    direction="row"
                    style={{ width: "100%" }}
                    align="stretch"
                >
                    <SimulationForm
                        isSimulationCompleted={isSimulationCompleted}
                        handleToggleView={handleToggleView}
                        showLimitShape={showLimitShape}
                        onSubmit={startSimulation}
                        isLoading={isLoading}
                        defaultParams={simulationParams}
                    />

                    <FlexBox
                        direction="column"
                        align="center"
                        style={{ flex: 2 }}
                    >
                        <FlexBox style={{ height: "100%", width: "100%" }}>
                            {error ? (
                                <FlexBox
                                    justify="center"
                                    align="center"
                                    style={{
                                        width: "100%",
                                        color: "var(--error-color)",
                                    }}
                                >
                                    {error}
                                </FlexBox>
                            ) : showLimitShape ? (
                                <FlexBox
                                    justify="center"
                                    align="center"
                                    style={{
                                        width: "100%",
                                        height: "100%",
                                    }}
                                >
                                    {isLoading ? (
                                        <p>Загрузка предельной формы...</p>
                                    ) : limitShapeImage ? (
                                        <img
                                            src={limitShapeImage}
                                            alt="Предельная форма диаграммы Юнга"
                                            style={{
                                                width: "100%",
                                                height: "567px",
                                                objectFit: "cover",
                                            }}
                                        />
                                    ) : (
                                        <p>
                                            Нажмите на кнопку "Показать
                                            предельную форму" для загрузки
                                            изображения
                                        </p>
                                    )}
                                </FlexBox>
                            ) : (
                                <VisualizationCanvas3D
                                    cells={cells}
                                    isLoading={isLoading}
                                    simulationParams={simulationParams}
                                />
                            )}
                        </FlexBox>
                    </FlexBox>
                </FlexBox>
            </FlexBox>
        </FlexBox>
    );
};

export default Simulator3D;
