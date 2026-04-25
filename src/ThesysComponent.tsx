import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import { useCallback, useEffect, ReactElement } from "react"
import { C1Component, ThemeProvider } from "@thesysai/genui-sdk"
import "@crayonai/react-ui/styles/index.css"

/**
 * A template for rendering Thesys C1 components within Streamlit
 * TODO: Add support for `theme`
 *
 * @param {ComponentProps} props - The props object passed from Streamlit
 * @param {Object} props.args - Custom arguments passed from the Python side
 * @param {string} props.args.c1Response - Response from a Thesys endpoint. Can be used with any response from Thesys.
 * @param {boolean} props.disabled - Whether the component is in a disabled state
 * @param {Object} props.theme - Streamlit theme object for consistent styling
 * @returns {ReactElement} The rendered component
 */
function ThesysComponent({ args, disabled }: ComponentProps): ReactElement {
  // Extract custom arguments passed from Python
  const { c1Response } = args

  /**
   * Tell Streamlit the height of this component
   * This ensures the component fits properly in the Streamlit app
   */
  useEffect(() => {
    // Call this when the component's size might change
    Streamlit.setFrameHeight()
  }, [args, disabled])

  const onC1Action = useCallback(
    (action: any) => {
      if (!disabled) {
        Streamlit.setComponentValue(action)
      }
    },
    [disabled]
  )

  return (
    <ThemeProvider>
      <C1Component
        c1Response={c1Response}
        isStreaming={false}
        onAction={onC1Action}
      />
    </ThemeProvider>
  )
}

/**
 * withStreamlitConnection is a higher-order component (HOC) that:
 * 1. Establishes communication between this component and Streamlit
 * 2. Passes Streamlit's theme settings to your component
 * 3. Handles passing arguments from Python to your component
 * 4. Handles component re-renders when Python args change
 *
 * You don't need to modify this wrapper unless you need custom connection behavior.
 */
export default withStreamlitConnection(ThesysComponent)
