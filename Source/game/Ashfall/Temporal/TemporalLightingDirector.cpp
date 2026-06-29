// ASHFALL — ATemporalLightingDirector implementation.
#include "TemporalLightingDirector.h"
#include "TemporalSubsystem.h"
#include "Engine/DirectionalLight.h"
#include "Components/DirectionalLightComponent.h"
#include "Engine/SkyLight.h"
#include "Components/SkyLightComponent.h"
#include "Engine/ExponentialHeightFog.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Engine/PostProcessVolume.h"
#include "EngineUtils.h"

ATemporalLightingDirector::ATemporalLightingDirector()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.bStartWithTickEnabled = false;

	// Fall = dim, orange, smoke-choked, desaturated with a red gain.
	FallMood.SunIntensity = 3.0f;
	FallMood.SunColor = FLinearColor(1.0f, 0.42f, 0.18f);
	FallMood.SkyIntensity = 0.3f;
	FallMood.FogDensity = 0.12f;
	FallMood.FogColor = FLinearColor(0.22f, 0.10f, 0.07f);
	FallMood.Saturation = 0.8f;
	FallMood.ColorGain = FLinearColor(1.15f, 0.72f, 0.55f);
	FallMood.ExposureBias = -0.55f;
}

void ATemporalLightingDirector::CacheSceneActors()
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	for (TActorIterator<ADirectionalLight> It(World); It && !Sun.IsValid(); ++It) { Sun = *It; }
	for (TActorIterator<ASkyLight> It(World); It && !Sky.IsValid(); ++It) { Sky = *It; }
	for (TActorIterator<AExponentialHeightFog> It(World); It && !Fog.IsValid(); ++It) { Fog = *It; }
	for (TActorIterator<APostProcessVolume> It(World); It && !PPV.IsValid(); ++It) { PPV = *It; }
}

void ATemporalLightingDirector::BeginPlay()
{
	Super::BeginPlay();
	CacheSceneActors();

	if (UWorld* World = GetWorld())
	{
		Subsystem = World->GetSubsystem<UTemporalSubsystem>();
		if (Subsystem.IsValid())
		{
			Subsystem->OnTimeStateChanged.AddDynamic(this, &ATemporalLightingDirector::HandleStateChanged);
			CurrentMood = (Subsystem->GetState() == ETimeState::Fall) ? FallMood : ZenithMood;
			ApplyMood(CurrentMood);
		}
	}
}

void ATemporalLightingDirector::HandleStateChanged(ETimeState NewState)
{
	TargetMood = (NewState == ETimeState::Fall) ? FallMood : ZenithMood;
	BlendElapsed = 0.0f;
	bBlending = true;
	SetActorTickEnabled(true);
}

FAshfallMood ATemporalLightingDirector::BlendMoods(const FAshfallMood& A, const FAshfallMood& B, float T)
{
	FAshfallMood M;
	M.SunIntensity = FMath::Lerp(A.SunIntensity, B.SunIntensity, T);
	M.SunColor = FMath::Lerp(A.SunColor, B.SunColor, T);
	M.SkyIntensity = FMath::Lerp(A.SkyIntensity, B.SkyIntensity, T);
	M.FogDensity = FMath::Lerp(A.FogDensity, B.FogDensity, T);
	M.FogColor = FMath::Lerp(A.FogColor, B.FogColor, T);
	M.Saturation = FMath::Lerp(A.Saturation, B.Saturation, T);
	M.ColorGain = FMath::Lerp(A.ColorGain, B.ColorGain, T);
	M.ExposureBias = FMath::Lerp(A.ExposureBias, B.ExposureBias, T);
	return M;
}

void ATemporalLightingDirector::ApplyMood(const FAshfallMood& Mood)
{
	if (Sun.IsValid())
	{
		if (UDirectionalLightComponent* C = Cast<UDirectionalLightComponent>(Sun->GetLightComponent()))
		{
			C->SetIntensity(Mood.SunIntensity);
			C->SetLightColor(Mood.SunColor);
		}
	}
	if (Sky.IsValid())
	{
		if (USkyLightComponent* C = Sky->GetLightComponent())
		{
			C->SetIntensity(Mood.SkyIntensity);
		}
	}
	if (Fog.IsValid())
	{
		if (UExponentialHeightFogComponent* C = Fog->GetComponent())
		{
			C->SetFogDensity(Mood.FogDensity);
			C->SetFogInscatteringColor(Mood.FogColor);
		}
	}
	if (PPV.IsValid())
	{
		FPostProcessSettings& S = PPV->Settings;
		S.bOverride_ColorSaturation = true;
		S.ColorSaturation = FVector4(Mood.Saturation, Mood.Saturation, Mood.Saturation, 1.0f);
		S.bOverride_ColorGain = true;
		S.ColorGain = FVector4(Mood.ColorGain.R, Mood.ColorGain.G, Mood.ColorGain.B, 1.0f);
		S.bOverride_AutoExposureBias = true;
		S.AutoExposureBias = Mood.ExposureBias;
	}
}

void ATemporalLightingDirector::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (!bBlending)
	{
		SetActorTickEnabled(false);
		return;
	}
	BlendElapsed += DeltaSeconds;
	const float T = (BlendTime > 0.0f) ? FMath::Clamp(BlendElapsed / BlendTime, 0.0f, 1.0f) : 1.0f;
	CurrentMood = BlendMoods(CurrentMood, TargetMood, T);
	ApplyMood(CurrentMood);
	if (T >= 1.0f)
	{
		CurrentMood = TargetMood;
		ApplyMood(CurrentMood);
		bBlending = false;
		SetActorTickEnabled(false);
	}
}
