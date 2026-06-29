// ASHFALL — AAshfallGameMode implementation.
#include "AshfallGameMode.h"
#include "AshfallCharacter.h"
#include "AshfallPlayerController.h"
#include "AshfallTemporalLibrary.h"
#include "Engine/Engine.h"
#include "GameFramework/Pawn.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "TimerManager.h"
#include "UObject/ConstructorHelpers.h"

AAshfallGameMode::AAshfallGameMode()
{
	// Use the template's visible third-person pawn for traversal (the temporal
	// toggle is pawn-agnostic — driven by the world subsystem). The combat-based
	// AAshfallCharacter requires a LifeBar widget set on a Blueprint, so it is
	// reserved for the action fail-state once that BP exists.
	static ConstructorHelpers::FClassFinder<APawn> PlayerPawnBP(
		TEXT("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter"));
	if (PlayerPawnBP.Succeeded())
	{
		DefaultPawnClass = PlayerPawnBP.Class;
	}
	else
	{
		DefaultPawnClass = AAshfallCharacter::StaticClass();
	}
	PlayerControllerClass = AAshfallPlayerController::StaticClass();
}

void AAshfallGameMode::BeginPlay()
{
	Super::BeginPlay();

	if (FParse::Param(FCommandLine::Get(), TEXT("AshfallAutoShot")))
	{
		// Give the world a few seconds to stream/compile shaders before capturing.
		FTimerHandle Handle;
		GetWorldTimerManager().SetTimer(Handle, this, &AAshfallGameMode::AutoShotStep, 6.0f, false);
	}
}

void AAshfallGameMode::AutoShotStep()
{
	UWorld* World = GetWorld();
	if (!GEngine || !World)
	{
		return;
	}

	switch (AutoShotIndex++)
	{
	case 0: GEngine->Exec(World, TEXT("HighResShot 1920x1080")); break;   // Zenith
	case 1: UAshfallTemporalLibrary::SetTimeState(this, ETimeState::Fall); break;
	case 2: GEngine->Exec(World, TEXT("HighResShot 1920x1080")); break;   // Fall
	case 3: GEngine->Exec(World, TEXT("quit")); break;
	default: return;
	}

	if (AutoShotIndex <= 3)
	{
		FTimerHandle Handle;
		GetWorldTimerManager().SetTimer(Handle, this, &AAshfallGameMode::AutoShotStep, 2.5f, false);
	}
}
