import React from "react";

export interface IFlexBoxProps extends React.HTMLAttributes<HTMLDivElement> {
    children?: React.ReactNode;
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
    gap?: number | string;
    rowGap?: number | string;
    columnGap?: number | string;
    flex?: number | string;
    width?: string | number;
    height?: string | number;
    padding?: number | string;
    margin?: number | string;
}

const FlexBox: React.FC<IFlexBoxProps> = ({
    children,
    direction = "row",
    justify = "flex-start",
    align = "flex-start",
    wrap = "nowrap",
    gap,
    rowGap,
    columnGap,
    flex,
    width,
    height,
    padding,
    margin,
    style,
    ...rest
}) => {
    const flexStyles: React.CSSProperties = {
        display: "flex",
        flexDirection: direction,
        justifyContent: justify,
        alignItems: align,
        flexWrap: wrap,
        flex: flex,
        width: typeof width === "number" ? `${width}px` : width,
        height: typeof height === "number" ? `${height}px` : height,
        padding: typeof padding === "number" ? `${padding}px` : padding,
        margin: typeof margin === "number" ? `${margin}px` : margin,
        ...style,
    };

    if (gap !== undefined) {
        flexStyles.gap = typeof gap === "number" ? `${gap}px` : gap;
    }

    if (rowGap !== undefined) {
        flexStyles.rowGap = typeof rowGap === "number" ? `${rowGap}px` : rowGap;
    }

    if (columnGap !== undefined) {
        flexStyles.columnGap =
            typeof columnGap === "number" ? `${columnGap}px` : columnGap;
    }

    return (
        <div style={flexStyles} {...rest}>
            {children}
        </div>
    );
};

export default FlexBox;
