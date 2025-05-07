import React from "react";
import FlexBox from "../ui-kit/FlexBox";
import { SimulationForm } from "../components/SimulationForm";
import { VisualizationCanvas2D } from "../components/VisualizationCanvas2D";
import { useSimulation2D } from "../hooks/useSimulation2D";
import Header from "../components/Header";

const Simulator2D: React.FC = () => {
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
    } = useSimulation2D();

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
                    <h1>2D Симулятор диаграмм Юнга</h1>
                    <p
                        className="text-muted"
                        style={{
                            margin: "0 auto",
                        }}
                    >
                        Настройте параметры и запустите симуляцию для
                        визуализации двумерных диаграмм Юнга
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
                        <FlexBox style={{ height: "600px", width: "100%" }}>
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
                                isLoading ? (
                                    <p>Загрузка предельной формы...</p>
                                ) : limitShapeImage ? (
                                    <div
                                        style={{
                                            width: "100%",
                                            minWidth: "100%",
                                            height: "600px",
                                            position: "relative",
                                            overflow: "hidden",
                                        }}
                                    >
                                        <img
                                            src={limitShapeImage}
                                            alt="Предельная форма диаграммы Юнга"
                                            style={{
                                                width: "100%",
                                                minWidth: "100%",
                                                height: "100%",
                                                objectFit: "cover",
                                                position: "absolute",
                                                top: 0,
                                                left: 0,
                                            }}
                                        />
                                    </div>
                                ) : (
                                    <p>
                                        Нажмите на кнопку "Показать предельную
                                        форму" для загрузки изображения
                                    </p>
                                )
                            ) : (
                                <VisualizationCanvas2D
                                    cells={cells}
                                    key={`2d-${showLimitShape}`}
                                    isVisible={!showLimitShape}
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

export default Simulator2D;
