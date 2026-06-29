// ASHFALL — UAshfallObjectiveSubsystem implementation.
#include "AshfallObjectiveSubsystem.h"
#include "AshfallSettings.h"
#include "game.h"

void UAshfallObjectiveSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
	if (const UAshfallSettings* Settings = GetDefault<UAshfallSettings>())
	{
		TotalToSave = FMath::Max(1, Settings->CitizensToSave);
	}
	SavedCount = 0;
	State = EObjectiveState::InProgress;
}

bool UAshfallObjectiveSubsystem::DoesSupportWorldType(const EWorldType::Type WorldType) const
{
	return WorldType == EWorldType::Game
		|| WorldType == EWorldType::PIE
		|| WorldType == EWorldType::Editor
		|| WorldType == EWorldType::EditorPreview;
}

void UAshfallObjectiveSubsystem::SaveCitizen()
{
	if (State != EObjectiveState::InProgress)
	{
		return;
	}
	SavedCount = FMath::Min(SavedCount + 1, TotalToSave);
	UE_LOG(Loggame, Log, TEXT("[Objective] citizen saved %d/%d"), SavedCount, TotalToSave);
	if (SavedCount >= TotalToSave)
	{
		State = EObjectiveState::Won;
		UE_LOG(Loggame, Log, TEXT("[Objective] WON — collapse averted"));
	}
	OnObjectiveChanged.Broadcast();
}

void UAshfallObjectiveSubsystem::FailObjective()
{
	if (State == EObjectiveState::InProgress)
	{
		State = EObjectiveState::Lost;
		OnObjectiveChanged.Broadcast();
	}
}

void UAshfallObjectiveSubsystem::ResetObjective()
{
	SavedCount = 0;
	State = EObjectiveState::InProgress;
	OnObjectiveChanged.Broadcast();
}
