import React, { useRef, useEffect } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { ICell2D } from "../hooks/useSimulation2D";
import FlexBox from "../ui-kit/FlexBox";

export interface IVisualizationCanvas3DProps {
    cells: ICell2D[];
    simulationParams: {
        steps: number;
        alpha: number;
        runs: number;
    };
    isLoading: boolean;
}

const VisualizationCanvas2D: React.FC<IVisualizationCanvas3DProps> = ({
    cells,
    simulationParams,
    isLoading,
}) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const sceneRef = useRef<THREE.Scene | null>(null);
    const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
    const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
    const controlsRef = useRef<OrbitControls | null>(null);
    const animationFrameRef = useRef<number | null>(null);
    const cubesRef = useRef<THREE.Mesh[]>([]);
    const pointLightRef = useRef<THREE.PointLight | null>(null);

    // Инициализация сцены
    useEffect(() => {
        if (!containerRef.current) return;

        // Создаем сцену
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xffffff); // Белый фон
        sceneRef.current = scene;

        // Создаем renderer
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        rendererRef.current = renderer;

        // Создаем камеру
        const camera = new THREE.PerspectiveCamera(
            60,
            containerRef.current.clientWidth /
                containerRef.current.clientHeight,
            0.1,
            1000
        );
        // Позиционируем камеру, чтобы получить лучший обзор диаграммы
        camera.position.set(15, 15, 15);
        camera.lookAt(0, 0, 0);
        cameraRef.current = camera;

        // Добавляем элемент canvas в DOM
        containerRef.current.appendChild(renderer.domElement);

        // Создаем контроллер для управления камерой
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.1;
        controls.rotateSpeed = 0.8;
        controls.zoomSpeed = 1.2;
        controlsRef.current = controls;

        // Создаем вспомогательную grid
        const gridHelper = new THREE.GridHelper(20, 20, 0x1e293b, 0x334155);
        scene.add(gridHelper);

        // Добавляем оси координат
        const axesHelper = new THREE.AxesHelper(5);
        scene.add(axesHelper);

        // Добавляем подписи к осям
        const createAxisLabel = (
            text: string,
            position: [number, number, number],
            color: number
        ) => {
            const canvas = document.createElement("canvas");
            canvas.width = 128;
            canvas.height = 64;
            const context = canvas.getContext("2d");
            if (context) {
                context.fillStyle = "#" + color.toString(16).padStart(6, "0");
                context.font = "Bold 48px Arial";
                context.fillText(text, 16, 48);

                const texture = new THREE.CanvasTexture(canvas);
                const material = new THREE.SpriteMaterial({
                    map: texture,
                    transparent: true,
                });
                const sprite = new THREE.Sprite(material);
                sprite.position.set(...position);
                sprite.scale.set(2, 1, 1);
                scene.add(sprite);
            }
        };

        // Добавляем подписи осей
        createAxisLabel("X", [6, 0, 0], 0xff0000);
        createAxisLabel("Y", [0, 6, 0], 0x00ff00);
        createAxisLabel("Z", [0, 0, 6], 0x0000ff);

        // Устанавливаем размер renderer
        handleResize();

        // Добавляем свет
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
        directionalLight.position.set(5, 10, 7);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 1024;
        directionalLight.shadow.mapSize.height = 1024;
        directionalLight.shadow.camera.near = 1;
        directionalLight.shadow.camera.far = 50;
        directionalLight.shadow.camera.left = -10;
        directionalLight.shadow.camera.right = 10;
        directionalLight.shadow.camera.top = 10;
        directionalLight.shadow.camera.bottom = -10;
        scene.add(directionalLight);

        // Добавляем точечный свет для эффекта свечения
        const pointLight = new THREE.PointLight(0x61dafb, 1, 15, 2);
        pointLight.position.set(0, 5, 0);
        pointLight.castShadow = true;
        scene.add(pointLight);
        pointLightRef.current = pointLight;

        // Запускаем анимацию
        const animate = () => {
            if (
                !rendererRef.current ||
                !sceneRef.current ||
                !cameraRef.current ||
                !controlsRef.current
            )
                return;

            animationFrameRef.current = requestAnimationFrame(animate);

            // Обновляем позицию точечного света для создания эффекта движения
            if (pointLightRef.current) {
                const time = Date.now() * 0.001;
                pointLightRef.current.position.x = Math.sin(time) * 8;
                pointLightRef.current.position.z = Math.cos(time) * 8;
            }

            // Обновляем контроллер
            controlsRef.current.update();

            // Рендерим сцену
            rendererRef.current.render(sceneRef.current, cameraRef.current);
        };

        animate();

        // Добавляем обработчик изменения размера окна
        window.addEventListener("resize", handleResize);

        // Очищаем ресурсы при размонтировании компонента
        return () => {
            window.removeEventListener("resize", handleResize);

            if (animationFrameRef.current) {
                cancelAnimationFrame(animationFrameRef.current);
            }

            // Очищаем все ссылки на объекты
            sceneRef.current = null;
            rendererRef.current = null;
            cameraRef.current = null;
            controlsRef.current = null;
            cubesRef.current = [];
        };
    }, [cells, containerRef]); // Сохраняем зависимость от cells, как было раньше

    // Функция для обработки изменения размера окна
    const handleResize = () => {
        if (!containerRef.current || !rendererRef.current || !cameraRef.current)
            return;

        const width = containerRef.current.clientWidth;
        const height = containerRef.current.clientHeight;

        rendererRef.current.setSize(width, height);
        cameraRef.current.aspect = width / height;
        cameraRef.current.updateProjectionMatrix();
    };

    // Обновляем сцену при изменении cells или visualizationType
    useEffect(() => {
        if (!sceneRef.current || !cells?.length) return;

        // Удаляем предыдущие кубы из сцены
        cubesRef.current.forEach((cube) => {
            if (sceneRef.current) {
                sceneRef.current.remove(cube);
            }
        });
        cubesRef.current = [];

        // Удаляем все существующие группы и метки из предыдущего рендера
        if (sceneRef.current) {
            const objectsToRemove: THREE.Object3D[] = [];
            sceneRef.current.traverse((object) => {
                if (
                    object instanceof THREE.Group ||
                    object instanceof THREE.Sprite
                ) {
                    objectsToRemove.push(object);
                }
            });
            objectsToRemove.forEach((object) => {
                sceneRef.current?.remove(object);
            });
        }

        // Определяем максимальные координаты для центрирования
        let maxX = 0;
        let maxY = 0;

        cells.forEach((cell) => {
            maxX = Math.max(maxX, cell.x);
            maxY = Math.max(maxY, cell.y);
        });

        // Получаем количество запусков из параметров симуляции
        const { runs } = simulationParams;

        // Модифицируем прозрачность в зависимости от количества запусков
        const opacityFactor = runs > 1 ? 1 / Math.sqrt(runs) : 1;

        // Группировка для всех кубов (для удобства центрирования)
        const cubesGroup = new THREE.Group();
        sceneRef.current.add(cubesGroup);

        // Геометрия куба для всех ячеек
        const geometry = new THREE.BoxGeometry(0.9, 0.9, 0.9);

        // Добавляем кубы на сцену
        cells.forEach((cell) => {
            // Создаем материал для куба с прозрачностью в зависимости от value
            const baseColor = new THREE.Color(0x38bdf8); // базовый цвет (голубой)

            // Создаем материал - заполненный куб (не wireframe)
            const cubeMaterial = new THREE.MeshPhysicalMaterial({
                color: baseColor,
                transparent: true,
                // Прозрачность зависит от значения ячейки и количества запусков
                opacity: Math.max(0.3, cell.value) * opacityFactor,
                metalness: 0.2, // слегка металлический эффект
                roughness: 0.5, // средняя шероховатость
                clearcoat: 0.3, // немного глянца
            });

            // Добавляем свечение для ячеек с высоким значением
            if (cell.value > 0.5) {
                cubeMaterial.emissive = baseColor.clone().multiplyScalar(0.3);
                cubeMaterial.emissiveIntensity = cell.value * 0.5;
            }

            const cube = new THREE.Mesh(geometry, cubeMaterial);

            // Позиционируем куб
            cube.position.set(
                cell.x - maxX / 2,
                cell.y, // Не вычитаем maxY/2, чтобы диаграмма росла вверх
                0
            );

            // Добавляем тени
            cube.castShadow = true;
            cube.receiveShadow = true;

            // Если runs > 1, добавляем текст с значением внутри куба (для отображения частоты)
            if (runs > 1 && cell.value > 0.5) {
                const displayValue = Math.round(cell.value * runs);
                if (displayValue > 0) {
                    // Создаем канвас с текстом
                    const canvas = document.createElement("canvas");
                    canvas.width = 64;
                    canvas.height = 64;
                    const context = canvas.getContext("2d");
                    if (context) {
                        context.fillStyle = "#ffffff";
                        context.font = "Bold 32px Arial";
                        context.textAlign = "center";
                        context.textBaseline = "middle";
                        context.fillText(displayValue.toString(), 32, 32);

                        // Создаем текстуру и материал
                        const texture = new THREE.CanvasTexture(canvas);
                        const spriteMaterial = new THREE.SpriteMaterial({
                            map: texture,
                            transparent: true,
                            opacity: Math.min(1, cell.value + 0.3),
                        });

                        // Создаем спрайт и позиционируем его внутри куба
                        const sprite = new THREE.Sprite(spriteMaterial);
                        sprite.scale.set(0.5, 0.5, 0.5);
                        sprite.position.copy(cube.position);
                        cubesGroup.add(sprite);
                    }
                }
            }

            cubesGroup.add(cube);
            cubesRef.current.push(cube);
        });

        // Перемещаем всю группу, чтобы нижняя плоскость диаграммы была на уровне сетки
        cubesGroup.position.y = 0;

        // Добавляем информационный текст о количестве запусков
        if (runs > 1) {
            const canvas = document.createElement("canvas");
            canvas.width = 256;
            canvas.height = 64;
            const context = canvas.getContext("2d");
            if (context) {
                context.fillStyle = "#94a3b8";
                context.font = "16px Arial";
                context.fillText(`Количество запусков: ${runs}`, 10, 30);

                const texture = new THREE.CanvasTexture(canvas);
                const material = new THREE.SpriteMaterial({
                    map: texture,
                    transparent: true,
                });
                const sprite = new THREE.Sprite(material);
                sprite.position.set(0, maxY + 3, 0);
                sprite.scale.set(5, 1.5, 1);
                sceneRef.current.add(sprite);
            }
        }

        // Ручное обновление рендера
        if (rendererRef.current && cameraRef.current && sceneRef.current) {
            rendererRef.current.render(sceneRef.current, cameraRef.current);
        }
    }, [cells, simulationParams]);

    return (
        <FlexBox
            direction="column"
            align="center"
            justify="center"
            className="visualization-container"
            style={{ width: "100%", height: "100%", position: "relative" }}
        >
            {isLoading ? (
                <FlexBox
                    direction="column"
                    align="center"
                    justify="center"
                    gap={16}
                    style={{ height: "100%" }}
                >
                    <div className="loading-dots">
                        <div></div>
                        <div></div>
                        <div></div>
                    </div>
                    <p className="text-muted">Выполняется симуляция...</p>
                </FlexBox>
            ) : cells?.length ? (
                <div
                    ref={containerRef}
                    style={{ width: "100%", height: "100%" }}
                />
            ) : (
                <FlexBox
                    direction="column"
                    align="center"
                    justify="center"
                    gap={16}
                    style={{ height: "100%" }}
                >
                    <p className="text-muted">
                        Настройте параметры и запустите симуляцию
                    </p>
                </FlexBox>
            )}

            {cells?.length > 0 && (
                <div
                    style={{
                        position: "absolute",
                        bottom: "10px",
                        left: "10px",
                        backgroundColor: "rgba(15, 23, 42, 0.7)",
                        padding: "8px 12px",
                        borderRadius: "4px",
                        zIndex: 10,
                        fontSize: "14px",
                    }}
                >
                    <p>Используйте мышь для вращения диаграммы:</p>
                    <ul style={{ margin: "5px 0", paddingLeft: "20px" }}>
                        <li>Левая кнопка: вращение</li>
                        <li>Колесо: масштабирование</li>
                        <li>Правая кнопка: перемещение</li>
                    </ul>
                </div>
            )}
        </FlexBox>
    );
};

export { VisualizationCanvas2D };
