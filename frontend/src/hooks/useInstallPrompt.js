import {
  useCallback,
  useEffect,
  useState,
} from "react";


const getStandaloneStatus =
  () => {

    const displayMode =
      window.matchMedia(
        "(display-mode: standalone)"
      ).matches;


    const iosStandalone =
      window.navigator
        ?.standalone ===
      true;


    return (
      displayMode ||
      iosStandalone
    );
  };


function useInstallPrompt() {

  const [
    deferredPrompt,
    setDeferredPrompt,
  ] = useState(null);


  const [
    isInstalled,
    setIsInstalled,
  ] = useState(
    getStandaloneStatus
  );


  useEffect(() => {

    const handleBeforeInstall =
      (
        event
      ) => {

        event.preventDefault();

        setDeferredPrompt(
          event
        );
      };


    const handleInstalled =
      () => {

        setDeferredPrompt(
          null
        );

        setIsInstalled(
          true
        );
      };


    window.addEventListener(
      "beforeinstallprompt",
      handleBeforeInstall
    );


    window.addEventListener(
      "appinstalled",
      handleInstalled
    );


    return () => {

      window.removeEventListener(
        "beforeinstallprompt",
        handleBeforeInstall
      );


      window.removeEventListener(
        "appinstalled",
        handleInstalled
      );
    };

  }, []);


  const requestInstall =
    useCallback(async () => {

      if (!deferredPrompt) {

        return {
          available:
            false,
        };
      }


      await deferredPrompt.prompt();


      const choice =
        await deferredPrompt
          .userChoice;


      setDeferredPrompt(
        null
      );


      if (
        choice?.outcome ===
        "accepted"
      ) {

        setIsInstalled(
          true
        );
      }


      return {

        available:
          true,

        outcome:
          choice?.outcome ||
          "unknown",
      };

    }, [
      deferredPrompt,
    ]);


  return {

    installAvailable:
      Boolean(
        deferredPrompt
      ),

    isInstalled,

    requestInstall,
  };
}


export default useInstallPrompt;