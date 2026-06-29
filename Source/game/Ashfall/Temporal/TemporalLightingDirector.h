// ASHFALL — drives the whole scene's mood between Zenith (warm afternoon) and
// Fall (ash-choked red gloom) when the time state toggles. Auto-finds the sun,
// sky light, height fog and post-process volume in the level on BeginPlay.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TemporalTypes.h"
#include "TemporalLightingDirector.generated.h"

class ADirectionalLight;
class ASkyLight;
class AExponentialHeightFog;
class APostProcessVolume;
class UTemporalSubsystem;

USTRUCT(BlueprintType)
struct FAshfallMood
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, Category = "Mood") float SunIntensity = 9.0f;
	UPROPERTY(EditAnywhere, Category = "Mood") FLinearColor SunColor = FLinearColor(1.0f, 0.96f, 0.90f);
	UPROPERTY(EditAnywhere, Category = "Mood") float SkyIntensity = 0.7f;
	UPROPERTY(EditAnywhere, Category = "Mood") float FogDensity = 0.015f;
	UPROPERTY(EditAnywhere, Category = "Mood") FLinearColor FogColor = FLinearColor(0.6f, 0.55f, 0.45f);
	UPROPERTY(EditAnywhere, Category = "Mood") float Saturation = 1.05f;
	UPROPERTY(EditAnywhere, Category = "Mood") FLinearColor ColorGain = FLinearColor(1.0f, 1.0f, 1.0f);
	UPROPERTY(EditAnywhere, Category = "Mood") float ExposureBias = -0.25f;
};

UCLASS()
class ATemporalLightingDirector : public AActor
{
	GENERATED_BODY()

public:
	ATemporalLightingDirector();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mood") FAshfallMood ZenithMood;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mood") FAshfallMood FallMood;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mood") float BlendTime = 1.5f;

protected:
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	UFUNCTION()
	void HandleStateChanged(ETimeState NewState);

	void CacheSceneActors();
	void ApplyMood(const FAshfallMood& Mood);
	static FAshfallMood BlendMoods(const FAshfallMood& A, const FAshfallMood& B, float T);

	TWeakObjectPtr<ADirectionalLight> Sun;
	TWeakObjectPtr<ASkyLight> Sky;
	TWeakObjectPtr<AExponentialHeightFog> Fog;
	TWeakObjectPtr<APostProcessVolume> PPV;
	TWeakObjectPtr<UTemporalSubsystem> Subsystem;

	FAshfallMood CurrentMood;
	FAshfallMood TargetMood;
	bool bBlending = false;
	float BlendElapsed = 0.0f;
};
