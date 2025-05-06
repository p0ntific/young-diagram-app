import React from "react";
import FlexBox from "../ui-kit/FlexBox";
import { Link } from "react-router-dom";
import Header from "../components/Header";

const HomePage: React.FC = () => {
    return (
        <FlexBox direction="column" style={{ minHeight: "100vh" }}>
            <Header />

            <FlexBox
                direction="column"
                align="center"
                gap={48}
                style={{
                    maxWidth: "1100px",
                    margin: "0 auto",
                    width: "100%",
                    padding: "48px 24px",
                }}
            >
                <section style={{ textAlign: "center", width: "100%" }}>
                    <FlexBox direction="column" align="center" gap={24}>
                        <h1>Симуляция диаграмм Юнга</h1>
                        <p
                            className="text-muted"
                            style={{
                                maxWidth: "700px",
                                fontSize: "1.1rem",
                                lineHeight: "1.7",
                            }}
                        >
                            Интерактивный инструмент для моделирования и
                            визуализации диаграмм Юнга в 2D и 3D пространствах
                        </p>
                    </FlexBox>
                </section>
                <section id="simulators" style={{ width: "100%" }}>
                    <h2 style={{ textAlign: "center", marginBottom: "24px" }}>
                        Выберите симулятор
                    </h2>
                    <div className="card-grid">
                        <Link
                            to="/2d"
                            className="card"
                            style={{ textDecoration: "none" }}
                        >
                            <div>
                                <h2>2D Симулятор</h2>
                                <p style={{ color: "var(--text-muted)" }}>
                                    Моделирование и визуализация двумерных
                                    диаграмм Юнга с различными параметрами
                                </p>

                                {/* Стилизованное изображение 2D диаграммы */}
                                <div
                                    style={{
                                        marginTop: "32px",
                                        display: "grid",
                                        gridTemplateColumns: "repeat(5, 1fr)",
                                        gridTemplateRows: "repeat(5, 1fr)",
                                        gap: "4px",
                                        height: "130px",
                                    }}
                                >
                                    {[...Array(5)].map((_, row) =>
                                        [...Array(5)].map((_, col) => {
                                            // Создаем пример диаграммы Юнга
                                            const shouldShow = col <= 4 - row;
                                            return (
                                                <div
                                                    key={`${row}-${col}`}
                                                    style={{
                                                        backgroundColor:
                                                            shouldShow
                                                                ? `rgba(255, 87, 51, ${
                                                                      1 -
                                                                      (col +
                                                                          row) *
                                                                          0.1
                                                                  })`
                                                                : "transparent",
                                                        borderRadius: "4px",
                                                        border: shouldShow
                                                            ? "1px solid rgba(255, 87, 51, 0.3)"
                                                            : "none",
                                                        opacity: shouldShow
                                                            ? 1
                                                            : 0,
                                                        boxShadow: shouldShow
                                                            ? "0 2px 8px rgba(255, 87, 51, 0.2)"
                                                            : "none",
                                                    }}
                                                />
                                            );
                                        })
                                    )}
                                </div>
                            </div>
                        </Link>

                        <Link
                            to="/3d"
                            className="card"
                            style={{ textDecoration: "none" }}
                        >
                            <div>
                                <h2>3D Симулятор</h2>
                                <p style={{ color: "var(--text-muted)" }}>
                                    Исследование трехмерных диаграмм Юнга с
                                    интерактивным управлением и визуализацией
                                </p>

                                {/* Стилизованное изображение 3D диаграммы */}
                                <div
                                    style={{
                                        marginTop: "32px",
                                        position: "relative",
                                        height: "130px",
                                        perspective: "600px",
                                    }}
                                >
                                    {[...Array(3)].map((_, z) => (
                                        <div
                                            key={`layer-${z}`}
                                            style={{
                                                position: "absolute",
                                                top: `${z * 12}px`,
                                                left: `${z * 12}px`,
                                                transform: `translateZ(${
                                                    -z * 20
                                                }px)`,
                                                display: "grid",
                                                gridTemplateColumns: `repeat(${
                                                    4 - z
                                                }, 1fr)`,
                                                gridTemplateRows: `repeat(${
                                                    4 - z
                                                }, 1fr)`,
                                                gap: "4px",
                                                width: `${(4 - z) * 28}px`,
                                                height: `${(4 - z) * 28}px`,
                                            }}
                                        >
                                            {[...Array(4 - z)].map((_, row) =>
                                                [...Array(4 - z)].map(
                                                    (_, col) => (
                                                        <div
                                                            key={`${z}-${row}-${col}`}
                                                            style={{
                                                                backgroundColor: `rgba(255, 87, 51, ${
                                                                    1 -
                                                                    (z +
                                                                        col +
                                                                        row) *
                                                                        0.1
                                                                })`,
                                                                borderRadius:
                                                                    "4px",
                                                                border: "1px solid rgba(255, 87, 51, 0.3)",
                                                                transform: `rotateX(45deg) rotateZ(45deg)`,
                                                                boxShadow:
                                                                    "0 2px 8px rgba(255, 87, 51, 0.2)",
                                                            }}
                                                        />
                                                    )
                                                )
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </Link>
                    </div>
                </section>
                <section
                    id="about"
                    className="visualization-container"
                    style={{ padding: "32px", width: "100%" }}
                >
                    <h2 style={{ marginBottom: "24px", textAlign: "center" }}>
                        О диаграммах Юнга
                    </h2>
                    <FlexBox
                        direction="column"
                        gap={24}
                        style={{
                            maxWidth: "800px",
                            margin: "0 auto",
                            lineHeight: "1.7",
                        }}
                    >
                        <p>
                            Диаграммы Юнга (также известные как диаграммы Ферре)
                            — это способ визуального представления разбиений
                            чисел. В двумерном случае они состоят из ячеек,
                            расположенных в виде левосторонних столбцов
                            невозрастающей высоты. Трехмерные диаграммы Юнга
                            представляют собой обобщение этой концепции на
                            пространство.
                        </p>

                        <blockquote
                            style={{
                                borderLeft: "3px solid var(--primary-color)",
                                paddingLeft: "24px",
                                margin: "16px 0",
                                fontStyle: "italic",
                                color: "var(--text-muted)",
                            }}
                        >
                            "Диаграммы Юнга представляют собой одну из самых
                            фундаментальных комбинаторных структур в математике,
                            с приложениями в алгебре, теории представлений и
                            математической физике."
                        </blockquote>

                        <div id="features">
                            <h3 style={{ marginBottom: "16px" }}>
                                Возможности проекта
                            </h3>
                            <ul
                                style={{
                                    paddingLeft: "20px",
                                    color: "var(--text-secondary)",
                                }}
                            >
                                <li>
                                    Симуляция роста случайных диаграмм с
                                    различными параметрами
                                </li>
                                <li>
                                    Множественные запуски симуляции для
                                    получения более точных результатов
                                </li>
                            </ul>
                        </div>
                    </FlexBox>
                </section>
            </FlexBox>
        </FlexBox>
    );
};

export default HomePage;
