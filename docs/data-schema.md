# Data Schema

`public/data/projects.json` が事業属性のcanonical datasetです。主なフィールドは `id`, `name`, `category`, `operator`, `department`, `municipalities`, `status`, `startFiscalYear`, `plannedCompletionFiscalYear`, `totalProjectCostMillionYen`, `progressPercent`, `benefitCostRatio`, `sources`, `provenance`, `locationAccuracy` です。

事業費は原則 **百万円** に正規化します。未確認値はnullです。

`public/data/projects.geojson` に表示用geometryを分離します。Point / LineString / Polygonをサポートし、Featureの `properties.projectId` はprojects.jsonの `id` と一致させます。

`locationAccuracy` は `official | derived | approximate | unknown`。`approximate` は代表点または公式位置図から読んだ概略位置であり、正確な施工区域として扱いません。
