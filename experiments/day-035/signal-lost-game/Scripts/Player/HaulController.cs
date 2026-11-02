using System;
using System.Collections.Generic;
using SignalLost.Debris;

namespace SignalLost.Player
{
    /// <summary>
    /// Plain, Unity-runtime-independent tracker of the parts the player is
    /// currently carrying. Owns no <see cref="UnityEngine.MonoBehaviour"/> state
    /// and is decoupled from movement/input, matching the pattern used by
    /// <c>SignalLost.Station.DecayTimer</c> and <c>SignalLost.Debris.SalvageSpot</c>,
    /// so it can be driven and unit-tested without the Unity runtime.
    ///
    /// Collecting a part from a <see cref="SalvageSpot"/> (Story 003) and acting
    /// on a delivered part to repair a system (Story 006) are both out of scope
    /// here — this class only tracks what is currently held and hands off
    /// whatever is held when delivery happens.
    /// </summary>
    public class HaulController
    {
        /// <summary>
        /// The maximum number of parts this controller can hold at once.
        /// Configured per instance (e.g. from a player stats asset) rather
        /// than hardcoded, so capacity can be tuned without touching code.
        /// </summary>
        public int MaxCapacity { get; }

        private readonly List<PartDefinition> heldParts;

        /// <summary>
        /// The parts currently held, in pickup order. Read-only for callers
        /// (e.g. a future UI showing carried parts); only this controller
        /// mutates the underlying collection.
        /// </summary>
        public IReadOnlyList<PartDefinition> HeldParts => heldParts;

        /// <summary>Current number of parts held. Readable by other systems (e.g. UI).</summary>
        public int HeldCount => heldParts.Count;

        /// <summary>True once <see cref="HeldCount"/> has reached <see cref="MaxCapacity"/>.</summary>
        public bool IsFull => heldParts.Count >= MaxCapacity;

        /// <summary>
        /// Creates a new haul controller with a fixed carry capacity.
        /// </summary>
        /// <param name="maxCapacity">
        /// The maximum number of parts this controller can hold at once. Must be
        /// greater than zero.
        /// </param>
        /// <example>
        /// <code>
        /// var haul = new HaulController(maxCapacity: 3);
        /// </code>
        /// </example>
        public HaulController(int maxCapacity)
        {
            if (maxCapacity <= 0)
            {
                throw new ArgumentOutOfRangeException(
                    nameof(maxCapacity),
                    maxCapacity,
                    "Max capacity must be greater than zero.");
            }

            MaxCapacity = maxCapacity;
            heldParts = new List<PartDefinition>();
        }

        /// <summary>
        /// Attempts to add a collected part to the held parts. Rejected (no-op)
        /// if already at <see cref="MaxCapacity"/>, or if <paramref name="part"/>
        /// is <c>null</c> — a <c>null</c> part (e.g. from
        /// <see cref="SalvageSpot.CollectPart"/> returning empty wreckage) means
        /// there is nothing to carry, so it is treated as a failed pickup rather
        /// than a successful no-op addition.
        /// </summary>
        /// <param name="part">The part to pick up.</param>
        /// <returns>True if the part was added, false if the pickup was rejected.</returns>
        /// <example>
        /// <code>
        /// PartDefinition collected = spot.CollectPart();
        /// if (!haul.TryPickUp(collected))
        /// {
        ///     // show "can't carry any more" / "nothing here" feedback
        /// }
        /// </code>
        /// </example>
        public bool TryPickUp(PartDefinition part)
        {
            if (part == null || IsFull)
            {
                return false;
            }

            heldParts.Add(part);
            return true;
        }

        /// <summary>
        /// Delivers all currently held parts, clearing them from this controller.
        /// What happens to the delivered parts (e.g. repairing a station system)
        /// is Story 006's responsibility, not this class's.
        /// </summary>
        /// <returns>
        /// The parts that were held at the moment of delivery, in pickup order.
        /// Empty if nothing was held.
        /// </returns>
        /// <example>
        /// <code>
        /// IReadOnlyList&lt;PartDefinition&gt; delivered = haul.DeliverAll();
        /// // Story 006 hands `delivered` to the repair action.
        /// </code>
        /// </example>
        public IReadOnlyList<PartDefinition> DeliverAll()
        {
            var delivered = heldParts.ToArray();
            heldParts.Clear();
            return delivered;
        }

        /// <summary>
        /// Removes one specific currently-held part (e.g. the part consumed by a
        /// successful repair in Story 006). No-op (returns false) if
        /// <paramref name="part"/> is <c>null</c> or not currently held.
        /// </summary>
        /// <param name="part">The exact part instance to remove.</param>
        /// <returns>True if the part was held and removed, false otherwise.</returns>
        /// <example>
        /// <code>
        /// if (haul.TryRemove(matchingPart))
        /// {
        ///     // part consumed by the repair action
        /// }
        /// </code>
        /// </example>
        public bool TryRemove(PartDefinition part)
        {
            if (part == null)
            {
                return false;
            }

            return heldParts.Remove(part);
        }
    }
}
