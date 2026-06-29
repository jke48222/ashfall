// ASHFALL — the single source of truth for the active time state in a world.
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "TemporalTypes.h"
#include "TemporalSubsystem.generated.h"

class UTemporalStateComponent;

/** Broadcast after the world's time state changes. */
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnTimeStateChanged, ETimeState, NewState);

/**
 *  Owns the current ETimeState for a world, notifies all registered temporal
 *  components, and stores "causal flags" — changes made in one state that
 *  resolve different outcomes in the other (the ripple at the heart of the game).
 */
UCLASS()
class UTemporalSubsystem : public UWorldSubsystem
{
	GENERATED_BODY()

public:
	/** Fires whenever the active state changes (after components are updated). */
	UPROPERTY(BlueprintAssignable, Category = "Temporal")
	FOnTimeStateChanged OnTimeStateChanged;

	UFUNCTION(BlueprintCallable, Category = "Temporal")
	ETimeState GetState() const { return CurrentState; }

	/** Sets the active state. No-op if already in that state unless bForce. */
	UFUNCTION(BlueprintCallable, Category = "Temporal")
	void SetState(ETimeState NewState, bool bForce = false);

	/** Flips Zenith <-> Fall. */
	UFUNCTION(BlueprintCallable, Category = "Temporal")
	void RequestToggle();

	/** Registration so the subsystem can push state to every temporal actor. */
	void RegisterComponent(UTemporalStateComponent* Component);
	void UnregisterComponent(UTemporalStateComponent* Component);

	// --- Causality ---------------------------------------------------------

	/** Sets/clears a named causal flag (e.g. "Vettii.StairCleared"). */
	UFUNCTION(BlueprintCallable, Category = "Temporal|Causality")
	void SetCausalFlag(FName Flag, bool bSet);

	/** True if the named causal flag is currently set. */
	UFUNCTION(BlueprintCallable, Category = "Temporal|Causality")
	bool HasCausalFlag(FName Flag) const;

	// --- USubsystem --------------------------------------------------------
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;
	/** Available in game, PIE and editor worlds so automation can drive it. */
	virtual bool DoesSupportWorldType(const EWorldType::Type WorldType) const override;

protected:
	UPROPERTY(VisibleAnywhere, Category = "Temporal")
	ETimeState CurrentState = ETimeState::Zenith;

	UPROPERTY()
	TArray<TWeakObjectPtr<UTemporalStateComponent>> RegisteredComponents;

	UPROPERTY()
	TSet<FName> CausalFlags;

	void BroadcastState(bool bImmediate);
};
