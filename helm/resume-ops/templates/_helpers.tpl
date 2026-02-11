{{- define "resume-ops.name" -}}
{{- .Chart.Name -}}
{{- end -}}

{{- define "resume-ops.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
