// ASHFALL — slice objective tracker: save N citizens to avert the collapse.
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "AshfallObjectiveSubsystem.generated.h"

UENUM(BlueprintType)
enum class EObjectiveState : uint8
{
	InProgress,
	Won,
	Lost
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnObjectiveChanged);

/**
 *  Tracks the vertical-slice win condition: rescue CitizensToSave citizens (read
 *  from UAshfallSettings) before the player is caught/downed. Pure state machine,
 *  driven by gameplay (rescue volumes, interactions) and testable headlessly.
 */
UCLASS()
class UAshfallObjectiveSubsystem : public UWorldSubsystem
{
	GENERATED_BODY()

public:
	/** Fires whenever saved count or objective state changes. */
	UPROPERTY(BlueprintAssignable, Category = "Ashfall|Objective")
	FOnObjectiveChanged OnObjectiveChanged;

	UFUNCTION(BlueprintCallable, Category = "Ashfall|Objective")
	void SaveCitizen();

	UFUNCTION(BlueprintCallable, Category = "Ashfall|Objective")
	void FailObjective();

	UFUNCTION(BlueprintCallable, Category = "Ashfall|Objective")
	void ResetObjective();

	UFUNCTION(BlueprintCallable, Category = "Ashfall|Objective")
	int32 GetCitizensSaved() const { return SavedCount; }

	UFUNCTION(BlueprintCallable, Category = "Ashfall|Objective")
	int32 GetCitizensTotal() const { return TotalToSave; }

	UFUNCTION(BlueprintCallable, Category = "Ashfall|Objective")
	EObjectiveState GetState() const { return State; }

	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual bool DoesSupportWorldType(const EWorldType::Type WorldType) const override;

protected:
	UPROPERTY(VisibleAnywhere, Category = "Ashfall|Objective")
	int32 TotalToSave = 6;

	UPROPERTY(VisibleAnywhere, Category = "Ashfall|Objective")
	int32 SavedCount = 0;

	UPROPERTY(VisibleAnywhere, Category = "Ashfall|Objective")
	EObjectiveState State = EObjectiveState::InProgress;
};
