import { type ComponentProps } from "solid-js"

const font = {
  "font-family": "Geist, Inter, ui-sans-serif, system-ui, sans-serif",
  "font-weight": 700,
  "letter-spacing": "0",
}

export const Mark = (props: { class?: string }) => {
  return (
    <svg
      data-component="logo-mark"
      classList={{ [props.class ?? ""]: !!props.class }}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <text
        x="12"
        y="17.5"
        text-anchor="middle"
        style={font}
        font-size="20"
        fill="var(--icon-strong-base)"
      >
        Z
      </text>
    </svg>
  )
}

export const Splash = (props: Pick<ComponentProps<"svg">, "ref" | "class">) => {
  return (
    <svg
      ref={props.ref}
      data-component="logo-splash"
      classList={{ [props.class ?? ""]: !!props.class }}
      viewBox="0 0 96 96"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <circle cx="48" cy="48" r="38" fill="var(--icon-weak-base)" opacity="0.16" />
      <text
        x="48"
        y="66"
        text-anchor="middle"
        style={font}
        font-size="56"
        fill="var(--icon-strong-base)"
      >
        Z
      </text>
    </svg>
  )
}

export const Logo = (props: { class?: string }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 320 72"
      fill="none"
      classList={{ [props.class ?? ""]: !!props.class }}
      role="img"
      aria-label="ZaneCode"
    >
      <text x="0" y="52" style={font} font-size="60" fill="var(--icon-strong-base)">
        ZaneCode
      </text>
    </svg>
  )
}
