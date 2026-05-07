import React, { useEffect, useRef } from "react";
import * as PIXI from "pixi.js";
import { Live2DModel } from "pixi-live2d-display-lipsyncpatch";

window.PIXI = PIXI;

export function Model({ isSpeaking, isThinking }) {
  const containerRef = useRef(null);
  const modelRef = useRef(null);

  // Handle motion based on state
  useEffect(() => {
    if (!modelRef.current) return;
    if (isSpeaking) {
      modelRef.current.motion("Tap");
    } else if (isThinking) {
      modelRef.current.motion("Idle");
    }
  }, [isSpeaking, isThinking]);

  // Sync to model ref for ticker access
  useEffect(() => {
    if (modelRef.current) {
      modelRef.current._isSpeaking = isSpeaking;
      modelRef.current._isThinking = isThinking;
    }
  }, [isSpeaking, isThinking]);

  useEffect(() => {
    const app = new PIXI.Application({
      backgroundAlpha: 0,
      autoDensity: true,
      resolution: window.devicePixelRatio || 1,
      antialias: true,
      eventMode: "static",
    });

    app.ticker.maxFPS = 30;

    if (containerRef.current) {
      containerRef.current.appendChild(app.view);
    }

    const modelUrl = "/models/miku_pro_jp/runtime/miku_sample_t04.model3.json";
    let isDisposed = false;
    let idleInterval = null;
    let lipSyncInterval = null;
    let mouthOpen = false;
    let tickerHandler = null;
    let contextMenuHandler = null;

    Live2DModel.from(modelUrl)
      .then((model) => {
        if (isDisposed) {
          model.destroy?.();
          return;
        }

        app.stage.addChild(model);
        modelRef.current = model;

        const desiredHeight = 450;
        const scale = desiredHeight / model.height;
        model.scale.set(scale);

        const mWidth = Math.round(model.width);
        const mHeight = Math.round(model.height);

        app.renderer.resize(mWidth, mHeight);

        model.anchor.set(0.65, 0.5);
        model.position.set(mWidth / 2, mHeight / 2);

        model.eventMode = "static";
        model.interactive = true;
        model.cursor = "pointer";

        model.on("pointerdown", (event) => {
          if (event.button === 0) {
            model.motion("Tap");
          } else if (event.button === 2) {
            const motion = ["FlickUp", "Flick"];
            const Random = Math.random();
            model.motion(Random > 0.5 ? motion[0] : motion[1]);
          }
        });

        contextMenuHandler = (e) => e.preventDefault();
        app.view.addEventListener("contextmenu", contextMenuHandler);

        if (window.electronAPI) {
          window.electronAPI.resizeWindow(mWidth * 0.45, mHeight * 0.65);
        }

        // Idle loop every 8 seconds
        idleInterval = setInterval(() => {
          if (
            !modelRef.current?._isSpeaking &&
            !modelRef.current?._isThinking
          ) {
            model.motion("Idle");
          }
        }, 8000);

        // Lipsync
        const startLipSync = () => {
          lipSyncInterval = setInterval(() => {
            mouthOpen = !mouthOpen;
            const value = mouthOpen ? Math.random() * 0.8 + 0.2 : 0;
            model.internalModel.coreModel.setParameterValueById(
              "ParamMouthOpenY",
              value,
            );
          }, 100);
        };

        const stopLipSync = () => {
          if (lipSyncInterval) {
            clearInterval(lipSyncInterval);
            lipSyncInterval = null;
          }
          model.internalModel.coreModel.setParameterValueById(
            "ParamMouthOpenY",
            0,
          );
        };

        tickerHandler = () => {
          if (modelRef.current?._isSpeaking && !lipSyncInterval) {
            startLipSync();
          } else if (!modelRef.current?._isSpeaking && lipSyncInterval) {
            stopLipSync();
          }
        };
        app.ticker.add(tickerHandler);
      })
      .catch((err) => {
        console.error("Error loading Live2D model:", err);
      });

    return () => {
      isDisposed = true;
      if (idleInterval) clearInterval(idleInterval);
      if (lipSyncInterval) clearInterval(lipSyncInterval);
      if (tickerHandler) app.ticker.remove(tickerHandler);
      if (contextMenuHandler) {
        app.view.removeEventListener("contextmenu", contextMenuHandler);
      }
      modelRef.current = null;
      app.destroy(true, { children: true, texture: true });
    };
  }, []);

  return <div ref={containerRef} style={{ lineHeight: 0 }} />;
}
