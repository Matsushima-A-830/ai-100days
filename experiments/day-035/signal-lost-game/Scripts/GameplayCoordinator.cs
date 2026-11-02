using System.Linq;
using SignalLost.Debris;
using SignalLost.Player;
using SignalLost.UI;
using UnityEngine;

namespace SignalLost
{
    /// <summary>
    /// Throwaway integration layer wiring the Signal Lost MVP systems
    /// (Stories 001-006) into one playable scene. NOT part of any story's
    /// formal scope — built on top of the already-tested domain classes
    /// (<see cref="DecayTimer"/>/<see cref="Station"/>/<see cref="HaulController"/>/
    /// <see cref="DebrisField"/>/<see cref="WinLossScreen"/>) to make the core
    /// loop playable end to end. Built by `Signal Lost > Setup Playable Scene`.
    /// </summary>
    public class GameplayCoordinator : MonoBehaviour
    {
        /// <summary>Simple scene-lifetime singleton so PlayerController/SalvageSpotView can reach shared state without inspector wiring.</summary>
        public static GameplayCoordinator Instance { get; private set; }

        [SerializeField] private float startingDecaySeconds = 180f;
        [SerializeField] private int playerCarryCapacity = 3;
        [SerializeField] private WinLossScreen winLossScreen;
        [SerializeField] private Transform stationTransform;

        public SignalLost.Station.DecayTimer DecayTimer { get; private set; }
        public SignalLost.Station.Station Station { get; private set; }
        public HaulController HaulController { get; private set; }
        public DebrisField DebrisField { get; private set; }
        public Transform StationTransform => stationTransform;
        public WinLossScreen WinLossScreen => winLossScreen;

        private void Awake()
        {
            Instance = this;

            DecayTimer = new SignalLost.Station.DecayTimer(startingDecaySeconds);
            Station = new SignalLost.Station.Station();
            HaulController = new HaulController(playerCarryCapacity);

            var spotViews = FindObjectsByType<SalvageSpotView>(FindObjectsSortMode.None);
            DebrisField = new DebrisField(spotViews.Select(v => v.Model));

            if (winLossScreen != null)
            {
                winLossScreen.Initialize(DecayTimer, Station);
            }

            // Same runtime-reassignment fix as SalvageSpotView/PlayerController:
            // a Sprite assigned by editor-time setup code can fail to survive
            // the domain reload on entering Play mode, leaving the station
            // invisible even though the GameObject and its SpriteRenderer exist.
            if (stationTransform != null && stationTransform.TryGetComponent(out SpriteRenderer stationRenderer))
            {
                var texture = Texture2D.whiteTexture;
                stationRenderer.sprite = Sprite.Create(
                    texture,
                    new Rect(0, 0, texture.width, texture.height),
                    new Vector2(0.5f, 0.5f),
                    texture.width);
                stationRenderer.color = new Color(0.3f, 0.35f, 0.4f);
                Debug.Log($"[GameplayCoordinator] station sprite reassigned = {stationRenderer.sprite != null}");
            }
            else
            {
                Debug.LogWarning("[GameplayCoordinator] stationTransform has no SpriteRenderer, or is unassigned.");
            }
        }

        private void Update()
        {
            if (winLossScreen != null && winLossScreen.IsRunOver)
            {
                return;
            }

            DecayTimer.Tick(Time.deltaTime);
        }

        private void OnGUI()
        {
            GUI.Label(new Rect(10, Screen.height - 50, 500, 40),
                $"Decay: {DecayTimer.RemainingSeconds:0.0}s   Held parts: {HaulController.HeldCount}/{HaulController.MaxCapacity}   (WASD/arrows move, Space interacts)");
        }
    }
}
