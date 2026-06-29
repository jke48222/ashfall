// ASHFALL — AAshfallPlayerController implementation.
#include "AshfallPlayerController.h"
#include "AshfallTemporalLibrary.h"
#include "TemporalSubsystem.h"

void AAshfallPlayerController::ToggleTimeState()
{
	const ETimeState NewState = UAshfallTemporalLibrary::ToggleTimeState(this);
	UE_LOG(LogTemp, Log, TEXT("[Ashfall] ToggleTimeState -> %s"),
		NewState == ETimeState::Fall ? TEXT("Fall") : TEXT("Zenith"));
}
