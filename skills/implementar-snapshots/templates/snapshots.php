<?php

// Ponto de partida para config/snapshots.php. Requer implementação dos consumidores.
// Inativo até revisão da política; os nomes de tabelas abaixo são sintéticos.
return [
    'enabled' => false,
    'project_id' => env('SNAPSHOT_PROJECT_ID'),
    'source_connection' => env('SNAPSHOT_SOURCE_CONNECTION'),
    'artifact_disk' => env('SNAPSHOT_ARTIFACT_DISK'),
    'artifact_prefix' => 'development-snapshots',
    'format_version' => 1,

    'create' => [
        'allowed_environments' => [],
        'window' => null,
        'rows_per_batch' => 500,
        'max_statement_bytes' => 4 * 1024 * 1024,
    ],

    'tables' => [
        'unclassified' => 'reject',
        'full_data' => ['accounts', 'users', 'migrations'],
        'schema_only' => ['jobs', 'sessions', 'personal_access_tokens'],
        'tiny_recent' => [
            'orders' => ['date_columns' => ['updated_at', 'created_at']],
            'order_items' => ['date_columns' => ['updated_at', 'created_at']],
        ],
    ],

    'tiny' => [
        'days' => 30,
        'timezone' => 'UTC',
        'missing_date_column' => 'reject',
        'null_date' => 'reject',
        'include_required_parents' => true,
        'row_limit' => 100000,
    ],

    'sanitization' => [
        'policy_version' => null,
        'require_reviewed_policy' => true,
    ],

    'application_files' => [
        'mode' => 'exclude',
    ],

    'restore' => [
        'allowed_environments' => ['local', 'testing'],
        'allowed_targets' => [],
        'require_expected_target' => true,
        'require_manifest' => true,
        'require_sha256' => true,
        'require_isolated_target' => true,
        'max_uncompressed_bytes' => 512 * 1024 * 1024,
        'max_statement_bytes' => 4 * 1024 * 1024,
    ],
];
