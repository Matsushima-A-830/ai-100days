using System;
using SignalLost.Debris;
using SignalLost.Player;

namespace SignalLost.Station
{
    /// <summary>
    /// Integration point for Story 006: ties together the held-part check
    /// (Story 004's <see cref="HaulController"/>), the system state change
    /// (Story 005's <see cref="RepairableSystem"/>) and the decay timer bonus
    /// (Story 001's <see cref="DecayTimer"/>) behind a single orchestrating
    /// call, per the brief's MVP feature 5. Plain, Unity-runtime-independent
    /// static class — no state of its own, so no instance is needed.
    /// </summary>
    public static class RepairAction
    {
        /// <summary>
        /// Seconds added to the decay timer's remaining time on a successful
        /// repair, per the brief's core loop ("each repaired system buys more
        /// time").
        /// </summary>
        public const float REPAIR_TIME_BONUS_SECONDS = 30f;

        /// <summary>
        /// Attempts to repair <paramref name="targetSystem"/> using a matching
        /// part currently held by <paramref name="haulController"/>. Rejected
        /// (returns false, no side effects) if the system is already repaired,
        /// or if no held part's <see cref="PartDefinition.TargetSystemName"/>
        /// matches <paramref name="targetSystem"/>'s name. On success, consumes
        /// exactly one matching part, marks the system repaired, and extends
        /// the decay timer by <see cref="REPAIR_TIME_BONUS_SECONDS"/>.
        /// </summary>
        /// <param name="targetSystem">The Offline system to attempt to repair.</param>
        /// <param name="haulController">The player's held-part tracker to consume from.</param>
        /// <param name="decayTimer">The station's decay timer to extend on success.</param>
        /// <returns>True if the repair succeeded, false if it was rejected.</returns>
        /// <example>
        /// <code>
        /// bool repaired = RepairAction.TryRepair(navigationSystem, haul, timer);
        /// if (!repaired)
        /// {
        ///     // show "missing part" / "already repaired" feedback
        /// }
        /// </code>
        /// </example>
        public static bool TryRepair(
            RepairableSystem targetSystem,
            HaulController haulController,
            DecayTimer decayTimer)
        {
            if (targetSystem == null)
            {
                throw new ArgumentNullException(nameof(targetSystem));
            }

            if (haulController == null)
            {
                throw new ArgumentNullException(nameof(haulController));
            }

            if (decayTimer == null)
            {
                throw new ArgumentNullException(nameof(decayTimer));
            }

            if (targetSystem.IsRepaired)
            {
                return false;
            }

            PartDefinition matchingPart = null;
            foreach (var part in haulController.HeldParts)
            {
                if (part != null && part.TargetSystemName == targetSystem.Name)
                {
                    matchingPart = part;
                    break;
                }
            }

            if (matchingPart == null)
            {
                return false;
            }

            if (!haulController.TryRemove(matchingPart))
            {
                return false;
            }

            targetSystem.MarkRepaired();
            decayTimer.ExtendTime(REPAIR_TIME_BONUS_SECONDS);
            return true;
        }
    }
}
