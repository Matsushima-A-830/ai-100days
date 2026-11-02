using System;
using SignalLost.Station;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UIElements;

namespace SignalLost.UI
{
    /// <summary>
    /// The outcome of a run, as shown by <see cref="WinLossScreen"/>.
    /// </summary>
    public enum WinLossOutcome
    {
        /// <summary>The run is still in progress; neither screen has been shown.</summary>
        None,
        /// <summary>All station systems were repaired before the decay timer expired.</summary>
        Win,
        /// <summary>The decay timer expired while at least one system was still offline.</summary>
        Loss
    }

    /// <summary>
    /// Thin presentation layer for the win/loss outcome (Story 002). Owns no
    /// win/loss logic of its own -- it only reacts to <see cref="DecayTimer.DecayComplete"/>
    /// (Story 001) and <see cref="Station.AllRepaired"/> (Story 005) and shows the
    /// matching UI Toolkit screen.
    ///
    /// Requires a <see cref="UIDocument"/> on the same GameObject, bound to a UXML
    /// document shaped like <c>WinLossScreen.uxml</c> (a root VisualElement containing
    /// a Label named "message-label" and a Button named "dismiss-button").
    ///
    /// A driving MonoBehaviour (from Stories 003/004/006, not yet built) owns the
    /// <see cref="DecayTimer"/> and <see cref="Station"/> instances and must call
    /// <see cref="Initialize"/> once to bind this screen to them:
    /// <code>
    /// winLossScreen.Initialize(myDecayTimer, myStation);
    /// </code>
    /// </summary>
    [RequireComponent(typeof(UIDocument))]
    public class WinLossScreen : MonoBehaviour
    {
        private const string MessageLabelName = "message-label";
        private const string DismissButtonName = "dismiss-button";
        private const string WinMessage = "SIGNAL RESTORED — all systems repaired.";
        private const string LossMessage = "SIGNAL LOST — the station has gone dark.";

        /// <summary>
        /// Fires when the player clicks the dismiss button. This component does not
        /// implement a scene reload or quit itself (out of scope for Story 002) --
        /// hook the actual restart/exit behaviour up to this event.
        /// </summary>
        public UnityEvent DismissRequested = new UnityEvent();

        /// <summary>The outcome currently shown, or <see cref="WinLossOutcome.None"/> if the run is still in progress.</summary>
        public WinLossOutcome CurrentOutcome { get; private set; } = WinLossOutcome.None;

        /// <summary>
        /// True once either the win or loss screen has been shown. Future scan/haul/repair
        /// input systems (Stories 003/004/006) should check this and stop processing input
        /// once it is true.
        /// </summary>
        public bool IsRunOver => CurrentOutcome != WinLossOutcome.None;

        private UIDocument uiDocument;
        private Label messageLabel;
        private Button dismissButton;
        private DecayTimer decayTimer;
        private Station.Station station;
        private bool isBound;

        private void Awake()
        {
            uiDocument = GetComponent<UIDocument>();
        }

        private void OnEnable()
        {
            // UIDocument builds its visual tree in its own OnEnable, and component
            // execution order does not guarantee that runs before this OnEnable, so
            // the root/Q<>() lookups and the button subscription live here rather
            // than in Awake to avoid querying a null rootVisualElement.
            VisualElement root = uiDocument.rootVisualElement;

            messageLabel = root?.Q<Label>(MessageLabelName);
            dismissButton = root?.Q<Button>(DismissButtonName);

            if (dismissButton != null)
            {
                dismissButton.clicked += HandleDismissClicked;
            }

            SetVisible(IsRunOver);
        }

        private void OnDisable()
        {
            if (dismissButton != null)
            {
                dismissButton.clicked -= HandleDismissClicked;
            }
        }

        /// <summary>
        /// Binds this screen to the run's decay timer and station. Must be called
        /// exactly once, before either source can fire its event.
        /// </summary>
        /// <param name="decayTimer">Story 001's countdown, whose <see cref="DecayTimer.DecayComplete"/> triggers the loss screen check.</param>
        /// <param name="station">Story 005's station, whose <see cref="Station.Station.AllRepaired"/> triggers the win screen.</param>
        public void Initialize(DecayTimer decayTimer, Station.Station station)
        {
            if (decayTimer == null) throw new ArgumentNullException(nameof(decayTimer));
            if (station == null) throw new ArgumentNullException(nameof(station));
            if (isBound) throw new InvalidOperationException("WinLossScreen.Initialize was already called; rebinding is not supported.");

            this.decayTimer = decayTimer;
            this.station = station;

            decayTimer.DecayComplete += HandleDecayComplete;
            station.AllRepaired += HandleAllRepaired;
            isBound = true;
        }

        private void HandleAllRepaired()
        {
            if (IsRunOver)
            {
                return;
            }

            ShowOutcome(WinLossOutcome.Win, WinMessage);
        }

        private void HandleDecayComplete()
        {
            if (IsRunOver)
            {
                return;
            }

            // Race guard: repair wins. Station.AllRepaired fires synchronously from
            // within the repair call that completes the last system, so in any driving
            // loop that repairs before ticking the timer in the same frame,
            // HandleAllRepaired above has already set IsRunOver by the time this runs.
            // The re-check below is a second line of defence in case a future driver
            // ticks the timer before processing that frame's repair: if every system
            // is already repaired, treat it as a win rather than a loss.
            if (station != null && station.AllSystemsRepaired)
            {
                return;
            }

            ShowOutcome(WinLossOutcome.Loss, LossMessage);
        }

        private void ShowOutcome(WinLossOutcome outcome, string message)
        {
            CurrentOutcome = outcome;

            if (messageLabel != null)
            {
                messageLabel.text = message;
            }

            SetVisible(true);
        }

        private void SetVisible(bool visible)
        {
            VisualElement root = uiDocument != null ? uiDocument.rootVisualElement : null;

            if (root != null)
            {
                root.style.display = visible ? DisplayStyle.Flex : DisplayStyle.None;
            }
        }

        private void HandleDismissClicked()
        {
            DismissRequested?.Invoke();
        }

        private void OnDestroy()
        {
            if (decayTimer != null)
            {
                decayTimer.DecayComplete -= HandleDecayComplete;
            }

            if (station != null)
            {
                station.AllRepaired -= HandleAllRepaired;
            }
        }
    }
}
