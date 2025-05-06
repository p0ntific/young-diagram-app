import { CSSProperties, MouseEventHandler, ReactNode } from "react";

interface IFlexBoxProps {
    children: ReactNode;
    direction?: "row" | "column" | "row-reverse" | "column-reverse";
    justify?:
        | "flex-start"
        | "flex-end"
        | "center"
        | "space-between"
        | "space-around"
        | "space-evenly";
    align?: "flex-start" | "flex-end" | "center" | "stretch" | "baseline";
    wrap?: "nowrap" | "wrap" | "wrap-reverse";
    gap?: string;
    width?: string;
    height?: string;
    padding?: string;
    margin?: string;
    className?: string;
    style?: CSSProperties;
    onClick?: MouseEventHandler<HTMLDivElement>;
}

export const FlexBox = ({
    children,
    direction = "row",
    justify = "flex-start",
    align = "center",
    wrap = "nowrap",
    gap = "0",
    width = "auto",
    height = "auto",
    padding = "0",
    margin = "0",
    className = "",
    style = {},
    onClick,
}: IFlexBoxProps) => {
    const baseStyle = {
        display: "flex",
        flexDirection: direction,
        justifyContent: justify,
        alignItems: align,
        flexWrap: wrap,
        gap,
        width,
        height,
        padding,
        margin,
        ...style,
    } as CSSProperties;

    return (
        <div style={baseStyle} className={className} onClick={onClick}>
            {children}
        </div>
    );
};
