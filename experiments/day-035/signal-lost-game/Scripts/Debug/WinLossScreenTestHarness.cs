using SignalLost.Station;
using SignalLost.UI;
using UnityEngine;

namespace SignalLost.DebugTools
{
    /// <summary>
    /// Throwaway manual-verification harness for Story 002 (win/loss screen).
    /// NOT part of any story's scope — exists only to let a developer trigger
    /// the win and loss screens on demand in Play mode for a screenshot.
    /// Wires up a fresh <see cref="DecayTimer"/> and <see cref="Station"/> and
    /// binds them to a <see cref="WinLossScreen"/> found in the scene.
    /// </summary>
    public class WinLossScreenTestHarness : MonoBehaviour
    {
        private DecayTimer decayTimer;
        private Station.Station station;
        private WinLossScreen winLossScreen;

        private void Start()
        {
            decayTimer = new DecayTimer(startingDurationSeconds: 300f);
            station = new Station.Station();

            winLossScreen = FindFirstObjectByType<WinLossScreen>();
            if (winLossScreen == null)
            {
                Debug.LogError("WinLossScreenTestHarness: no WinLossScreen found in the scene.");
                return;
            }

            winLossScreen.Initialize(decayTimer, station);
        }

        private void Update()
        {
            if (winLossScreen == null)
            {
                return;
            }

            if (Input.GetKeyDown(KeyCode.W))
            {
                ForceWin();
            }
            else if (Input.GetKeyDown(KeyCode.L))
            {
                ForceLoss();
            }
        }

        private void ForceWin()
        {
            foreach (var system in station.Systems)
            {
                system.MarkRepaired();
            }
        }

        private void ForceLoss()
        {
            // Drive RemainingSeconds to zero: ExtendTime is the only way to move
            // it from outside DecayTimer, so push it far negative, then Tick to
            // let the class clamp to zero and fire DecayComplete itself.
            decayTimer.ExtendTime(-999999f);
            decayTimer.Tick(0.01f);
        }

        private void OnGUI()
        {
            GUI.Label(new Rect(10, 10, 400, 60),
                "WinLossScreen test harness\nPress W to force a win, L to force a loss.");
        }
    }
}
