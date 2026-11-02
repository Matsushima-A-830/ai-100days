using System;

namespace SignalLost.Station
{
    /// <summary>
    /// Plain, Unity-runtime-independent countdown representing the station's
    /// orbital decay. Owns no <see cref="UnityEngine.MonoBehaviour"/> state so it
    /// can be driven by any update loop (and unit-tested without the Unity
    /// runtime, once a test project exists).
    ///
    /// A driver (e.g. a <c>MonoBehaviour</c> elsewhere) is expected to call
    /// <see cref="Tick"/> once per frame with its own delta time:
    /// <code>
    /// var timer = new DecayTimer(startingDurationSeconds: 120f);
    /// timer.DecayComplete += () => Debug.Log("Station lost.");
    ///
    /// // In a MonoBehaviour's Update():
    /// timer.Tick(Time.deltaTime);
    /// </code>
    /// </summary>
    public class DecayTimer
    {
        /// <summary>
        /// Decay rate applied when no explicit rate is supplied to the
        /// constructor: one second of remaining time lost per second elapsed.
        /// </summary>
        public const float DEFAULT_DECAY_RATE = 1f;

        /// <summary>
        /// The duration, in seconds, this timer was configured to start from.
        /// Does not change as the timer ticks down; useful for computing a
        /// 0-1 progress ratio for UI display.
        /// </summary>
        public float StartingDuration { get; }

        /// <summary>
        /// Seconds of decay remaining. Clamped to zero once expired.
        /// </summary>
        public float RemainingSeconds { get; private set; }

        /// <summary>
        /// Multiplier applied to elapsed time each <see cref="Tick"/>.
        /// A value of 1 decays in real time; above 1 decays faster;
        /// below 1 (but above zero) decays slower.
        /// </summary>
        public float DecayRate { get; private set; }

        /// <summary>
        /// True once <see cref="RemainingSeconds"/> has reached zero and
        /// <see cref="DecayComplete"/> has fired.
        /// </summary>
        public bool HasExpired { get; private set; }

        /// <summary>
        /// Fires exactly once, the moment <see cref="RemainingSeconds"/>
        /// reaches zero. Other systems (e.g. the win/loss screen in Story 002)
        /// subscribe to this to react to the station's decay completing.
        /// <code>
        /// timer.DecayComplete += HandleStationLost;
        /// </code>
        /// </summary>
        public event Action DecayComplete;

        /// <summary>
        /// Creates a new countdown.
        /// </summary>
        /// <param name="startingDurationSeconds">
        /// The duration, in seconds, the timer counts down from. Must be
        /// greater than zero.
        /// </param>
        /// <param name="decayRate">
        /// Multiplier applied to elapsed time each tick. Defaults to
        /// <see cref="DEFAULT_DECAY_RATE"/> (real-time decay). Must not be
        /// negative.
        /// </param>
        /// <example>
        /// <code>
        /// var timer = new DecayTimer(startingDurationSeconds: 180f);
        /// </code>
        /// </example>
        public DecayTimer(float startingDurationSeconds, float decayRate = DEFAULT_DECAY_RATE)
        {
            if (startingDurationSeconds <= 0f)
            {
                throw new ArgumentOutOfRangeException(
                    nameof(startingDurationSeconds),
                    startingDurationSeconds,
                    "Starting duration must be greater than zero.");
            }

            if (decayRate < 0f)
            {
                throw new ArgumentOutOfRangeException(
                    nameof(decayRate),
                    decayRate,
                    "Decay rate must not be negative.");
            }

            StartingDuration = startingDurationSeconds;
            RemainingSeconds = startingDurationSeconds;
            DecayRate = decayRate;
            HasExpired = false;
        }

        /// <summary>
        /// Advances the countdown by <paramref name="deltaTime"/> seconds of
        /// real time (scaled by <see cref="DecayRate"/>). No-ops once the
        /// timer has already expired. Fires <see cref="DecayComplete"/>
        /// exactly once, the tick that brings <see cref="RemainingSeconds"/>
        /// to zero or below.
        /// </summary>
        /// <param name="deltaTime">Elapsed real time, in seconds, since the last tick.</param>
        /// <example>
        /// <code>
        /// void Update() => timer.Tick(Time.deltaTime);
        /// </code>
        /// </example>
        public void Tick(float deltaTime)
        {
            if (HasExpired)
            {
                return;
            }

            RemainingSeconds -= deltaTime * DecayRate;

            if (RemainingSeconds <= 0f)
            {
                RemainingSeconds = 0f;
                HasExpired = true;
                DecayComplete?.Invoke();
            }
        }

        /// <summary>
        /// Adds (or removes, if negative) seconds from the remaining time.
        /// Intended hook for Story 006's repair action. No-ops once the
        /// timer has already expired.
        /// </summary>
        /// <param name="additionalSeconds">Seconds to add to the remaining time.</param>
        /// <example>
        /// <code>
        /// // A successful repair buys the station 30 more seconds.
        /// timer.ExtendTime(30f);
        /// </code>
        /// </example>
        public void ExtendTime(float additionalSeconds)
        {
            if (HasExpired)
            {
                return;
            }

            RemainingSeconds += additionalSeconds;
        }

        /// <summary>
        /// Sets a new decay rate multiplier. Intended hook for Story 006's
        /// repair action (e.g. slowing decay after a repair). No-ops once the
        /// timer has already expired.
        /// </summary>
        /// <param name="newRate">
        /// The new multiplier applied to elapsed time each tick. Must not be negative.
        /// </param>
        /// <example>
        /// <code>
        /// // A repair halves the decay rate for the rest of the run.
        /// timer.AdjustDecayRate(timer.DecayRate * 0.5f);
        /// </code>
        /// </example>
        public void AdjustDecayRate(float newRate)
        {
            if (HasExpired)
            {
                return;
            }

            if (newRate < 0f)
            {
                throw new ArgumentOutOfRangeException(
                    nameof(newRate),
                    newRate,
                    "Decay rate must not be negative.");
            }

            DecayRate = newRate;
        }
    }
}
