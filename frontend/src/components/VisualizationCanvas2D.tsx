import React, { useRef, useEffect } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { ICell2D } from "../hooks/useSimulation2D"; // Assuming this path is okay
import FlexBox from "../ui-kit/FlexBox"; // Assuming this path is okay

export interface IVisualizationCanvas2DProps {
    // Renamed from IVisualizationCanvas3DProps
    cells: ICell2D[];
    simulationParams: {
        steps: number;
        alpha: number;
        runs: number;
    };
    isLoading: boolean;
    isVisible: boolean; // This prop dictates if the component's content should be active
}

const VisualizationCanvas2D: React.FC<IVisualizationCanvas2DProps> = ({
    cells,
    isVisible,
    simulationParams,
    isLoading,
}) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const sceneRef = useRef<THREE.Scene | null>(null);
    const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
    const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
    const controlsRef = useRef<OrbitControls | null>(null);
    const animationFrameRef = useRef<number | null>(null);
    const cubesGroupRef = useRef<THREE.Group | null>(null); // To hold all cubes + value sprites
    const pointLightRef = useRef<THREE.PointLight | null>(null);
    const runsInfoSpriteRef = useRef<THREE.Sprite | null>(null);

    // Initialization and re-initialization of the scene
    useEffect(() => {
        if (!isVisible || !containerRef.current) {
            // If not visible or container not ready, do nothing.
            // Cleanup will handle stopping animation if it was running.
            return;
        }

        // If already initialized, no need to re-init unless major props change
        // This effect will re-run if isVisible becomes true *after* being false,
        // or if containerRef changes (which it shouldn't after first mount unless component remounts).
        // Or, if you want to re-init on cells/simulationParams change, add them to dependency array.
        // However, for now, we assume full remount or isVisible toggle handles it.

        console.log("Initializing Three.js scene...");

        const currentContainer = containerRef.current;

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xffffff);
        sceneRef.current = scene;

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        rendererRef.current = renderer;

        currentContainer.appendChild(renderer.domElement);

        const camera = new THREE.PerspectiveCamera(
            60,
            currentContainer.clientWidth / currentContainer.clientHeight,
            0.1,
            1000
        );
        camera.position.set(15, 15, 15);
        camera.lookAt(0, 0, 0);
        cameraRef.current = camera;

        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.1;
        controls.rotateSpeed = 0.8;
        controls.zoomSpeed = 1.2;
        controlsRef.current = controls;

        const gridHelper = new THREE.GridHelper(20, 20, 0x1e293b, 0x334155);
        scene.add(gridHelper);

        const axesHelper = new THREE.AxesHelper(5);
        scene.add(axesHelper);

        // Axis labels (consider making them optional or smaller)
        const createAxisLabel = (
            text: string,
            position: [number, number, number],
            colorHex: number
        ) => {
            // Simplified: For brevity, this part is okay but can be componentized
            const canvas = document.createElement("canvas");
            canvas.width = 128;
            canvas.height = 64;
            const context = canvas.getContext("2d");
            if (context) {
                context.fillStyle =
                    "#" + colorHex.toString(16).padStart(6, "0");
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
        createAxisLabel("X", [6, 0, 0], 0xff0000);
        createAxisLabel("Y", [0, 6, 0], 0x00ff00);
        createAxisLabel("Z", [0, 0, 6], 0x0000ff);

        const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
        directionalLight.position.set(5, 10, 7);
        // ... (shadow properties for directionalLight)
        scene.add(directionalLight);

        const pointLight = new THREE.PointLight(0x61dafb, 1, 15, 2);
        pointLight.position.set(0, 5, 0);
        pointLight.castShadow = true;
        scene.add(pointLight);
        pointLightRef.current = pointLight;

        const groupForAllCubes = new THREE.Group();
        scene.add(groupForAllCubes);
        cubesGroupRef.current = groupForAllCubes;

        const handleResize = () => {
            if (!rendererRef.current || !cameraRef.current || !currentContainer)
                return;
            const width = currentContainer.clientWidth;
            const height = currentContainer.clientHeight;
            rendererRef.current.setSize(width, height);
            cameraRef.current.aspect = width / height;
            cameraRef.current.updateProjectionMatrix();
        };

        handleResize(); // Initial size
        window.addEventListener("resize", handleResize);

        const animate = () => {
            if (
                !rendererRef.current ||
                !sceneRef.current ||
                !cameraRef.current ||
                !controlsRef.current
            )
                return;
            animationFrameRef.current = requestAnimationFrame(animate);

            if (pointLightRef.current) {
                const time = Date.now() * 0.001;
                pointLightRef.current.position.x = Math.sin(time) * 8;
                pointLightRef.current.position.z = Math.cos(time) * 8;
            }

            controlsRef.current.update();
            rendererRef.current.render(sceneRef.current, cameraRef.current);
        };

        animate();

        return () => {
            console.log("Cleaning up Three.js scene...");
            window.removeEventListener("resize", handleResize);

            if (animationFrameRef.current) {
                cancelAnimationFrame(animationFrameRef.current);
                animationFrameRef.current = null;
            }

            if (controlsRef.current) {
                controlsRef.current.dispose();
                controlsRef.current = null;
            }

            // Dispose scene objects
            if (sceneRef.current) {
                // Remove all children explicitly, including helpers, lights, groups
                while (sceneRef.current.children.length > 0) {
                    const object = sceneRef.current.children[0];
                    sceneRef.current.remove(object);
                    // If object is a mesh/sprite, dispose geometry/material
                    if (
                        object instanceof THREE.Mesh ||
                        object instanceof THREE.Sprite
                    ) {
                        if (object.geometry) object.geometry.dispose();
                        if (object.material) {
                            if (Array.isArray(object.material)) {
                                object.material.forEach((material) =>
                                    material.dispose()
                                );
                            } else if (object.material.map) {
                                // for SpriteMaterial, PointsMaterial
                                object.material.map?.dispose();
                                object.material.dispose();
                            } else {
                                object.material.dispose();
                            }
                        }
                    }
                    // If object is a light that casts shadow, dispose shadow map
                    if (
                        object instanceof THREE.Light &&
                        object.shadow &&
                        object.shadow.map
                    ) {
                        object.shadow.map.dispose();
                    }
                }
                // Axes labels also need to be cleaned if they are not part of children removed above
                // For simplicity, assuming above loop handles them, or they are few. Scene itself is cleared.
                sceneRef.current = null;
            }

            if (rendererRef.current) {
                // Important: remove canvas from DOM
                if (
                    rendererRef.current.domElement.parentNode ===
                    currentContainer
                ) {
                    currentContainer.removeChild(
                        rendererRef.current.domElement
                    );
                }
                rendererRef.current.dispose(); // Dispose WebGL context and resources
                rendererRef.current = null;
            }

            cameraRef.current = null;
            pointLightRef.current = null;
            cubesGroupRef.current = null;
            runsInfoSpriteRef.current = null;
        };
    }, [isVisible]); // Re-initialize if isVisible becomes true

    // Effect to update cubes when cells or simulationParams change
    useEffect(() => {
        if (!isVisible || !sceneRef.current || !cubesGroupRef.current || !cells)
            return;

        const group = cubesGroupRef.current;
        // Clear previous cubes and sprites from the group
        while (group.children.length > 0) {
            const child = group.children[0];
            group.remove(child);
            if (child instanceof THREE.Mesh) {
                child.geometry?.dispose();
                if (Array.isArray(child.material))
                    child.material.forEach((m) => m.dispose());
                else child.material?.dispose();
            } else if (child instanceof THREE.Sprite) {
                child.material.map?.dispose();
                child.material.dispose();
            }
        }

        let maxY = 0;
        cells.forEach((cell) => {
            maxY = Math.max(maxY, cell.y);
        });

        const { runs } = simulationParams;
        const opacityFactor = runs > 1 ? 1 / Math.sqrt(runs) : 1;
        const geometry = new THREE.BoxGeometry(0.9, 0.9, 0.9);

        cells.forEach((cell) => {
            const baseColor = new THREE.Color(0x38bdf8);
            const cubeMaterial = new THREE.MeshPhysicalMaterial({
                color: baseColor,
                transparent: true,
                opacity: Math.max(0.1, cell.value) * opacityFactor, // ensure some visibility
                metalness: 0.2,
                roughness: 0.5,
                clearcoat: 0.3,
            });

            if (cell.value > 0.5) {
                cubeMaterial.emissive = baseColor.clone().multiplyScalar(0.3);
                cubeMaterial.emissiveIntensity = cell.value * 0.5;
            }

            const cube = new THREE.Mesh(geometry, cubeMaterial);
            cube.position.set(cell.x, cell.y, 0);
            cube.castShadow = true;
            cube.receiveShadow = true;
            group.add(cube);

            if (runs > 1 && cell.value > 0.1) {
                // Show for significant values
                const displayValue = Math.round(cell.value * runs);
                if (displayValue > 0) {
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
                        const texture = new THREE.CanvasTexture(canvas);
                        const spriteMaterial = new THREE.SpriteMaterial({
                            map: texture,
                            transparent: true,
                            opacity: Math.min(1, cell.value + 0.3),
                            depthTest: false, // Render on top
                            depthWrite: false,
                        });
                        const sprite = new THREE.Sprite(spriteMaterial);
                        sprite.scale.set(0.5, 0.5, 0.5);
                        sprite.position.copy(cube.position);
                        sprite.position.z += 0.5; // Slightly in front of cube face
                        group.add(sprite);
                    }
                }
            }
        });

        // Add/Update runs info text
        if (runsInfoSpriteRef.current) {
            sceneRef.current.remove(runsInfoSpriteRef.current);
            runsInfoSpriteRef.current.material.map?.dispose();
            runsInfoSpriteRef.current.material.dispose();
            runsInfoSpriteRef.current = null;
        }

        if (runs > 1) {
            const canvas = document.createElement("canvas");
            canvas.width = 256;
            canvas.height = 64;
            const context = canvas.getContext("2d");
            if (context) {
                context.fillStyle = "#334155"; // Darker color for better visibility
                context.font = "Bold 20px Arial";
                context.fillText(`Количество запусков: ${runs}`, 10, 30);
                const texture = new THREE.CanvasTexture(canvas);
                const material = new THREE.SpriteMaterial({
                    map: texture,
                    transparent: true,
                    depthTest: false,
                });
                const sprite = new THREE.Sprite(material);
                // Position above the diagram
                sprite.position.set(0, maxY + 2, 0);
                sprite.scale.set(5, 1.25, 1);
                sceneRef.current.add(sprite);
                runsInfoSpriteRef.current = sprite;
            }
        }

        // Manually trigger a render if animation loop might not be running or to see immediate changes
        if (
            rendererRef.current &&
            sceneRef.current &&
            cameraRef.current &&
            !animationFrameRef.current
        ) {
            rendererRef.current.render(sceneRef.current, cameraRef.current);
        }
    }, [cells, simulationParams, isVisible]); // Rerun if these change and component is visible

    return (
        <FlexBox
            direction="column"
            align="center"
            justify="center"
            className="visualization-container"
            style={{
                width: "100%",
                height: "100%",
                position: "relative",
            }}
        >
            {isLoading &&
                isVisible && ( // Show loader only if supposed to be visible
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
                )}

            <div
                ref={containerRef}
                style={{
                    width: "100%",
                    height: "100%",
                    display: isVisible && !isLoading ? "block" : "none", // Hide canvas container during load or if not visible
                    outline: "none", // For focus if needed
                }}
                tabIndex={0} // For keyboard events if needed
            />
            {isVisible && !isLoading && cells?.length > 0 && (
                <div
                    style={{
                        position: "absolute",
                        bottom: "10px",
                        left: "10px",
                        backgroundColor: "rgba(0,0,0,0.5)",
                        color: "white",
                        padding: "5px",
                        borderRadius: "3px",
                        fontSize: "0.8em",
                    }}
                >
                    <p style={{ margin: 0 }}>
                        Используйте мышь для вращения диаграммы:
                    </p>
                    <ul style={{ margin: 0, paddingLeft: "20px" }}>
                        <li>Левая кнопка: вращение</li>
                        <li>Колесо: масштабирование</li>
                        <li>Правая кнопка: перемещение</li>
                    </ul>
                </div>
            )}
        </FlexBox>
    );
};

export { VisualizationCanvas2D }; // Keep export name consistent with import in Simulator2D
