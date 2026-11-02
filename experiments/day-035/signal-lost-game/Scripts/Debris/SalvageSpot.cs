namespace SignalLost.Debris
{
    /// <summary>
    /// Lifecycle states of a <see cref="SalvageSpot"/>. A spot only ever moves
    /// forward: <see cref="Available"/> -> <see cref="Revealed"/> -> <see cref="Depleted"/>.
    /// </summary>
    public enum SalvageSpotState
    {
        /// <summary>Not yet scanned; whether it holds a part is unknown to the player.</summary>
        Available,

        /// <summary>Scanned; its part (if any) is now visible and can be collected.</summary>
        Revealed,

        /// <summary>Its part has been collected (or it had none); nothing more can happen here.</summary>
        Depleted
    }

    /// <summary>
    /// A single point of wreckage in a <see cref="DebrisField"/> that the player can
    /// scan and, once revealed, collect a part from. Plain, Unity-runtime-independent
    /// state (no <see cref="UnityEngine.MonoBehaviour"/>), matching the pattern used
    /// by <c>SignalLost.Station.DecayTimer</c>, so the logic can be driven and
    /// unit-tested without the Unity runtime.
    ///
    /// Collecting a part here only means handing off the <see cref="PartDefinition"/>
    /// reference and marking the spot depleted; carrying/hauling it (Story 004) and
    /// using it to repair a system (Story 006) are out of scope for this class.
    /// </summary>
    public class SalvageSpot
    {
        /// <summary>
        /// The part this spot holds, or <c>null</c> for wreckage that turns out to
        /// be empty once scanned.
        /// </summary>
        public PartDefinition Part { get; }

        /// <summary>True if this spot has a part to offer (regardless of current state).</summary>
        public bool HasPart => Part != null;

        /// <summary>Current lifecycle state of this spot.</summary>
        public SalvageSpotState State { get; private set; }

        /// <summary>
        /// Creates a new salvage spot, starting in the <see cref="SalvageSpotState.Available"/> state.
        /// </summary>
        /// <param name="part">
        /// The part this spot holds, or <c>null</c> for empty wreckage that will
        /// still be scannable but yields nothing.
        /// </param>
        public SalvageSpot(PartDefinition part = null)
        {
            Part = part;
            State = SalvageSpotState.Available;
        }

        /// <summary>
        /// Reveals this spot. Transitions <see cref="SalvageSpotState.Available"/> to
        /// <see cref="SalvageSpotState.Revealed"/>. No-ops (does not change state) if
        /// this spot has already been scanned or depleted.
        /// </summary>
        /// <returns>True if this spot holds a usable part, false if it is empty.</returns>
        /// <example>
        /// <code>
        /// if (spot.Scan())
        /// {
        ///     // show pickup prompt for spot.Part
        /// }
        /// </code>
        /// </example>
        public bool Scan()
        {
            if (State == SalvageSpotState.Available)
            {
                State = SalvageSpotState.Revealed;
            }

            return HasPart;
        }

        /// <summary>
        /// Claims this spot's part. Transitions <see cref="SalvageSpotState.Revealed"/>
        /// to <see cref="SalvageSpotState.Depleted"/>. Fails gracefully (returns
        /// <c>null</c>, no state change) if this spot has not yet been scanned or has
        /// already been depleted.
        /// </summary>
        /// <returns>
        /// The collected <see cref="PartDefinition"/>, or <c>null</c> if there was
        /// nothing to collect (not revealed yet, already depleted, or the spot was
        /// empty).
        /// </returns>
        /// <example>
        /// <code>
        /// PartDefinition collected = spot.CollectPart();
        /// </code>
        /// </example>
        public PartDefinition CollectPart()
        {
            if (State != SalvageSpotState.Revealed)
            {
                return null;
            }

            State = SalvageSpotState.Depleted;
            return Part;
        }
    }
}
