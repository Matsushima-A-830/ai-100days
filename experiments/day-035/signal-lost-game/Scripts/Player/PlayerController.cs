using SignalLost.Debris;
using SignalLost.Station;
using UnityEngine;

namespace SignalLost.Player
{
    /// <summary>
    /// Throwaway playable-scene controller — NOT part of any story's formal
    /// scope. Moves the player and lets them interact with salvage spots and
    /// the station using the already-tested domain classes from Stories
    /// 003-006. Built by `Signal Lost > Setup Playable Scene`.
    /// </summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public class PlayerController : MonoBehaviour
    {
        [SerializeField] private float moveSpeed = 4f;
        [SerializeField] private float interactRange = 1.25f;

        private void Awake()
        {
            var spriteRenderer = GetComponent<SpriteRenderer>();

            if (spriteRenderer.sprite == null)
            {
                var texture = Texture2D.whiteTexture;
                spriteRenderer.sprite = Sprite.Create(
                    texture,
                    new Rect(0, 0, texture.width, texture.height),
                    new Vector2(0.5f, 0.5f),
                    texture.width);
            }

            spriteRenderer.color = new Color(0.2f, 0.6f, 0.9f);
        }

        private void Update()
        {
            var coordinator = GameplayCoordinator.Instance;
            if (coordinator == null ||
                (coordinator.WinLossScreen != null && coordinator.WinLossScreen.IsRunOver))
            {
                return;
            }

            float horizontal = Input.GetAxisRaw("Horizontal");
            float vertical = Input.GetAxisRaw("Vertical");
            transform.Translate(new Vector3(horizontal, vertical, 0f) * moveSpeed * Time.deltaTime);

            if (Input.GetKeyDown(KeyCode.Space))
            {
                Debug.Log("[PlayerController] Space pressed — interacting.");
                Interact(coordinator);
            }
        }

        private void Interact(GameplayCoordinator coordinator)
        {
            var spotViews = FindObjectsByType<SalvageSpotView>(FindObjectsSortMode.None);
            SalvageSpotView nearestSpot = null;
            float nearestDistance = interactRange;

            foreach (var spot in spotViews)
            {
                float distance = Vector3.Distance(transform.position, spot.transform.position);
                Debug.Log($"[PlayerController] spot {spot.name} at distance {distance:0.00} (range {interactRange})");
                if (distance <= nearestDistance)
                {
                    nearestSpot = spot;
                    nearestDistance = distance;
                }
            }

            if (nearestSpot != null)
            {
                Debug.Log($"[PlayerController] interacting with nearest spot {nearestSpot.name} (state: {nearestSpot.Model.State})");
                InteractWithSpot(nearestSpot, coordinator);
                return;
            }

            if (coordinator.StationTransform != null)
            {
                float stationDistance = Vector3.Distance(transform.position, coordinator.StationTransform.position);
                Debug.Log($"[PlayerController] station distance {stationDistance:0.00} (range {interactRange})");
                if (stationDistance <= interactRange)
                {
                    InteractWithStation(coordinator);
                    return;
                }
            }

            Debug.Log("[PlayerController] nothing in range to interact with.");
        }

        private void InteractWithSpot(SalvageSpotView spotView, GameplayCoordinator coordinator)
        {
            var model = spotView.Model;

            switch (model.State)
            {
                case SalvageSpotState.Available:
                    model.Scan();
                    Debug.Log($"[PlayerController] scanned {spotView.name} — now {model.State}, holds a part: {model.HasPart}");
                    break;

                case SalvageSpotState.Revealed:
                    var part = model.CollectPart();
                    if (part != null)
                    {
                        bool picked = coordinator.HaulController.TryPickUp(part);
                        Debug.Log($"[PlayerController] collected {part.DisplayName} from {spotView.name} — picked up: {picked}");
                    }
                    break;

                case SalvageSpotState.Depleted:
                    Debug.Log($"[PlayerController] {spotView.name} is already depleted.");
                    break;
            }
        }

        private void InteractWithStation(GameplayCoordinator coordinator)
        {
            // Try every system: RepairAction.TryRepair safely no-ops for any
            // system the player isn't carrying a matching part for, or that's
            // already repaired, so one press repairs everything it can.
            foreach (var system in coordinator.Station.Systems)
            {
                RepairAction.TryRepair(system, coordinator.HaulController, coordinator.DecayTimer);
            }
        }
    }
}
