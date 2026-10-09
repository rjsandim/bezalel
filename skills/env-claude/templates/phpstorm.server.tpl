      <server host="${SVC_HOST}" id="${SERVER_ID}" name="${SERVER_NAME}" port="443" use_path_mappings="true">
        <path_mappings>
          <mapping local-root="$PROJECT_DIR$/${FOLDER}" remote-root="/app" />
        </path_mappings>
      </server>
