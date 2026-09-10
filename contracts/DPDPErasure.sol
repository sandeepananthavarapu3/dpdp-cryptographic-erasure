// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DPDPErasure {
    address public centralAuthority;

    // Structure to hold file metadata and access logs
    struct FileRecord {
        string fileId;
        address uploader;
        bool isDeleted;
        uint256 uploadTimestamp;
        uint256 deletionTimestamp;
    }

    // Maps a File ID to its Record
    mapping(string => FileRecord) public files;

    // Events for immutable logging (The "Audit Trail")
    event FileUploaded(string fileId, address uploader, uint256 timestamp);
    event AccessRequested(string fileId, address requester, uint256 timestamp);
    event DeletionTriggered(string fileId, uint256 timestamp);

    // Modifier to restrict actions to the Central Authority (Backend API)
    modifier onlyAuthority() {
        require(msg.sender == centralAuthority, "Unauthorized: Only Central Authority allowed");
        _;
    }

    constructor() {
        // The wallet that deploys the contract becomes the Central Authority
        centralAuthority = msg.sender;
    }

    // 1. Register a new file upload
    function registerFile(string memory _fileId) public {
        require(files[_fileId].uploadTimestamp == 0, "File ID already exists");

        files[_fileId] = FileRecord({
            fileId: _fileId,
            uploader: msg.sender,
            isDeleted: false,
            uploadTimestamp: block.timestamp,
            deletionTimestamp: 0
        });

        emit FileUploaded(_fileId, msg.sender, block.timestamp);
    }

    // 2. Request Access to Shares
    function requestAccess(string memory _fileId) public {
        require(files[_fileId].uploadTimestamp != 0, "File does not exist");
        require(!files[_fileId].isDeleted, "Access Denied: Data has been cryptographically erased");
        
        // Log the access request (could add more complex authorization logic here)
        emit AccessRequested(_fileId, msg.sender, block.timestamp);
    }

    // 3. Trigger Right to Erasure
    function triggerDeletion(string memory _fileId) public onlyAuthority {
        require(files[_fileId].uploadTimestamp != 0, "File does not exist");
        require(!files[_fileId].isDeleted, "File is already deleted");

        // Mark as deleted and record the timestamp
        files[_fileId].isDeleted = true;
        files[_fileId].deletionTimestamp = block.timestamp;

        // Broadcast the deletion command to the Node network
        emit DeletionTriggered(_fileId, block.timestamp);
    }

    // 4. Verify File Status (Useful for DPDP Audits)
    function checkStatus(string memory _fileId) public view returns (bool exists, bool deleted) {
        return (files[_fileId].uploadTimestamp != 0, files[_fileId].isDeleted);
    }
}
