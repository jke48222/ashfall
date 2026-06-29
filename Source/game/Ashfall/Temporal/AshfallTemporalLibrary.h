// ASHFALL — Blueprint/Python-callable access to the temporal subsystem.
// Used by designers (Blueprints) and by headless automation/tests (Python).
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "TemporalTypes.h"
#include "AshfallTemporalLibrary.generated.h"

class UTemporalSubsystem;

UCLASS()
class UAshfallTemporalLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/** Returns the temporal subsystem for the context object's world (may be null). */
	UFUNCTION(BlueprintCallable, Category = "Ashfall|Temporal", meta = (WorldContext = "WorldContextObject"))
	static UTemporalSubsystem* GetTemporalSubsystem(const UObject* WorldContextObject);

	/** Flips Zenith <-> Fall and returns the resulting state. */
	UFUNCTION(BlueprintCallable, Category = "Ashfall|Temporal", meta = (WorldContext = "WorldContextObject"))
	static ETimeState ToggleTimeState(const UObject* WorldContextObject);

	UFUNCTION(BlueprintCallable, Category = "Ashfall|Temporal", meta = (WorldContext = "WorldContextObject"))
	static ETimeState GetTimeState(const UObject* WorldContextObject);

	UFUNCTION(BlueprintCallable, Category = "Ashfall|Temporal", meta = (WorldContext = "WorldContextObject"))
	static void SetTimeState(const UObject* WorldContextObject, ETimeState NewState);

	UFUNCTION(BlueprintCallable, Category = "Ashfall|Temporal|Causality", meta = (WorldContext = "WorldContextObject"))
	static void SetCausalFlag(const UObject* WorldContextObject, FName Flag, bool bSet);

	UFUNCTION(BlueprintCallable, Category = "Ashfall|Temporal|Causality", meta = (WorldContext = "WorldContextObject"))
	static bool HasCausalFlag(const UObject* WorldContextObject, FName Flag);

	// --- Objective (slice win condition) -----------------------------------

	UFUNCTION(BlueprintCallable, Category = "Ashfall|Objective", meta = (WorldContext = "WorldContextObject"))
	static void SaveCitizen(const UObject* WorldContextObject);

	UFUNCTION(BlueprintCallable, Category = "Ashfall|Objective", meta = (WorldContext = "WorldContextObject"))
	static int32 GetCitizensSaved(const UObject* WorldContextObject);

	UFUNCTION(BlueprintCallable, Category = "Ashfall|Objective", meta = (WorldContext = "WorldContextObject"))
	static int32 GetCitizensTotal(const UObject* WorldContextObject);

	UFUNCTION(BlueprintCallable, Category = "Ashfall|Objective", meta = (WorldContext = "WorldContextObject"))
	static bool IsObjectiveWon(const UObject* WorldContextObject);
};
