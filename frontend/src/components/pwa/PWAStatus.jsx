import {
  useEffect,
  useState,
} from "react";

import {
  Download,
  RefreshCw,
  Wifi,
  WifiOff,
  X,
} from "lucide-react";

import {
  useRegisterSW,
} from "virtual:pwa-register/react";

import useInstallPrompt
  from "../../hooks/useInstallPrompt";

import "../../styles/PWA.css";


function PWAStatus() {

  const [
    isOnline,
    setIsOnline,
  ] = useState(
    navigator.onLine
  );


  const {
    installAvailable,
    isInstalled,
    requestInstall,
  } =
    useInstallPrompt();


  const {
    offlineReady:
      [
        offlineReady,
        setOfflineReady,
      ],

    needRefresh:
      [
        needRefresh,
        setNeedRefresh,
      ],

    updateServiceWorker,
  } =
    useRegisterSW();


  useEffect(() => {

    const handleOnline =
      () =>
        setIsOnline(
          true
        );


    const handleOffline =
      () =>
        setIsOnline(
          false
        );


    window.addEventListener(
      "online",
      handleOnline
    );


    window.addEventListener(
      "offline",
      handleOffline
    );


    return () => {

      window.removeEventListener(
        "online",
        handleOnline
      );


      window.removeEventListener(
        "offline",
        handleOffline
      );
    };

  }, []);


  return (
    <div className="pwa-status-container">

      {!isOnline && (

        <div className="pwa-toast pwa-toast-warning">

          <WifiOff
            size={19}
          />

          <div>

            <strong>
              You are offline
            </strong>

            <span>
              Cached screens may remain available,
              but detection and cloud data require
              an internet connection.
            </span>

          </div>

        </div>

      )}


      {isOnline && offlineReady && (

        <div className="pwa-toast">

          <Wifi
            size={19}
          />

          <div>

            <strong>
              Offline shell ready
            </strong>

            <span>
              BreedVision application files are
              cached for faster reopening.
            </span>

          </div>


          <button
            type="button"
            className="pwa-close-button"
            onClick={() =>
              setOfflineReady(
                false
              )
            }
          >

            <X
              size={17}
            />

          </button>

        </div>

      )}


      {needRefresh && (

        <div className="pwa-toast pwa-toast-update">

          <RefreshCw
            size={19}
          />

          <div>

            <strong>
              New version available
            </strong>

            <span>
              Reload BreedVision to use the
              latest application version.
            </span>

          </div>


          <div className="pwa-toast-actions">

            <button
              type="button"
              onClick={() =>
                updateServiceWorker(
                  true
                )
              }
            >
              Update
            </button>


            <button
              type="button"
              className="pwa-close-button"
              onClick={() =>
                setNeedRefresh(
                  false
                )
              }
            >

              <X
                size={16}
              />

            </button>

          </div>

        </div>

      )}


      {
        installAvailable &&
        !isInstalled && (

          <div className="pwa-toast pwa-toast-install">

            <Download
              size={19}
            />

            <div>

              <strong>
                Install BreedVision
              </strong>

              <span>
                Add the application to your
                device for a standalone
                mobile-style experience.
              </span>

            </div>


            <button
              type="button"
              className="pwa-install-button"
              onClick={
                requestInstall
              }
            >
              Install
            </button>

          </div>

        )
      }

    </div>
  );
}


export default PWAStatus;