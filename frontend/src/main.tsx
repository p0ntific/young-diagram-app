import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import HomePage from "./pages/HomePage";
import Simulator2D from "./pages/Simulator2D";
import Simulator3D from "./pages/Simulator3D";
import "./styles.css";

const router = createBrowserRouter([
    {
        path: "/",
        element: <HomePage />,
    },
    {
        path: "/2d",
        element: <Simulator2D />,
    },
    {
        path: "/3d",
        element: <Simulator3D />,
    },
]);

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
    <React.StrictMode>
        <RouterProvider router={router} />
    </React.StrictMode>
);
