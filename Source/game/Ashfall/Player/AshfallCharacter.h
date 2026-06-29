// ASHFALL — the Chronomason. Inherits camera + combat + health from
// ACombatCharacter (10% action fail-state) and adds the temporal control verb.
#pragma once

#include "CoreMinimal.h"
#include "CombatCharacter.h"
#include "AshfallCharacter.generated.h"

class UTemporalControlComponent;

UCLASS()
class AAshfallCharacter : public ACombatCharacter
{
	GENERATED_BODY()

public:
	AAshfallCharacter();

	FORCEINLINE UTemporalControlComponent* GetTemporalControl() const { return TemporalControl; }

protected:
	/** Owns the time-toggle verb (cooldown + focus). */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Temporal", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UTemporalControlComponent> TemporalControl;
};
