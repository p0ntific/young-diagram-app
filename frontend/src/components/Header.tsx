import React from "react";
import { Link, useLocation } from "react-router-dom";
import FlexBox from "../ui-kit/FlexBox";

// Компонент заголовка без зависимости от useLocation
const Header: React.FC = () => {
    const { pathname } = useLocation();

    // Функция проверки активного пути
    const isActive = (path: string) => pathname === path;

    return (
        <FlexBox
            direction="row"
            justify="space-between"
            align="center"
            padding={16}
            gap={24}
            style={{
                border: `1px solid var(--border-color)`,
                borderRadius: "16px",
                background: "var(--bg-surface)",
                boxShadow: "0 4px 16px rgba(0, 0, 0, 0.3)",
                position: "sticky",
                top: 0,
                left: "50%",
                transform: "translateX(-50%)",
                zIndex: 100,
            }}
        >
            <Link
                to="/"
                className="logo"
                style={{
                    textDecoration: "none",
                    color: "white",
                    fontWeight: "bold",
                    fontSize: "1.5rem",
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                }}
            >
                <div
                    style={{
                        width: "32px",
                        height: "32px",
                        display: "grid",
                        gridTemplateColumns: "repeat(3, 1fr)",
                        gridTemplateRows: "repeat(3, 1fr)",
                        gap: "2px",
                    }}
                >
                    {/* Визуализация простой диаграммы Юнга в логотипе с новыми цветами */}
                    <div
                        style={{
                            backgroundColor: "var(--primary-color)",
                            borderRadius: "2px",
                        }}
                    ></div>
                    <div
                        style={{
                            backgroundColor: "var(--primary-color)",
                            borderRadius: "2px",
                            opacity: 0.8,
                        }}
                    ></div>
                    <div
                        style={{
                            backgroundColor: "var(--primary-color)",
                            borderRadius: "2px",
                            opacity: 0.6,
                        }}
                    ></div>
                    <div
                        style={{
                            backgroundColor: "var(--primary-color)",
                            borderRadius: "2px",
                            opacity: 0.8,
                        }}
                    ></div>
                    <div
                        style={{
                            backgroundColor: "var(--primary-color)",
                            borderRadius: "2px",
                            opacity: 0.6,
                        }}
                    ></div>
                    <div style={{ backgroundColor: "transparent" }}></div>
                    <div
                        style={{
                            backgroundColor: "var(--primary-color)",
                            borderRadius: "2px",
                            opacity: 0.6,
                        }}
                    ></div>
                    <div style={{ backgroundColor: "transparent" }}></div>
                    <div style={{ backgroundColor: "transparent" }}></div>
                </div>
                <span>YoungDiagrams</span>
            </Link>

            <FlexBox gap={24} align="center">
                <Link
                    to="/"
                    style={{
                        textDecoration: "none",
                        color: isActive("/")
                            ? "var(--primary-color)"
                            : "var(--text-primary)",
                        position: "relative",
                        padding: "8px 0",
                        fontWeight: 500,
                    }}
                >
                    {isActive("/") && (
                        <div
                            style={{
                                position: "absolute",
                                bottom: 0,
                                left: 0,
                                width: "100%",
                                height: "2px",
                                background:
                                    "linear-gradient(to right, var(--gradient-start), var(--gradient-end))",
                                borderRadius: "2px",
                            }}
                        ></div>
                    )}
                    Главная
                </Link>

                <Link
                    to="/2d"
                    style={{
                        textDecoration: "none",
                        color: isActive("/2d")
                            ? "var(--primary-color)"
                            : "var(--text-primary)",
                        position: "relative",
                        padding: "8px 0",
                        fontWeight: 500,
                    }}
                >
                    {isActive("/2d") && (
                        <div
                            style={{
                                position: "absolute",
                                bottom: 0,
                                left: 0,
                                width: "100%",
                                height: "2px",
                                background:
                                    "linear-gradient(to right, var(--gradient-start), var(--gradient-end))",
                                borderRadius: "2px",
                            }}
                        ></div>
                    )}
                    2D Симулятор
                </Link>

                <Link
                    to="/3d"
                    style={{
                        textDecoration: "none",
                        color: isActive("/3d")
                            ? "var(--primary-color)"
                            : "var(--text-primary)",
                        position: "relative",
                        padding: "8px 0",
                        fontWeight: 500,
                    }}
                >
                    {isActive("/3d") && (
                        <div
                            style={{
                                position: "absolute",
                                bottom: 0,
                                left: 0,
                                width: "100%",
                                height: "2px",
                                background:
                                    "linear-gradient(to right, var(--gradient-start), var(--gradient-end))",
                                borderRadius: "2px",
                            }}
                        ></div>
                    )}
                    3D Симулятор
                </Link>
            </FlexBox>
        </FlexBox>
    );
};

export default Header;
