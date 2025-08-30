/**
 * 仓库绑定组件 - Codex风格
 */
import { useState, useEffect, useRef } from 'react';
import { gitlabService, backendService } from '../lib/api';
import { useRepositoryBinding } from '../hooks/useProjects';
import styles from '../page.module.css';

const RepositoryBinding = ({ onRepositoryBound }) => {
  const [inputValue, setInputValue] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [ownRepositories, setOwnRepositories] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [selectedRepository, setSelectedRepository] = useState(null);
  const [boundRepositoryIds, setBoundRepositoryIds] = useState([]); // 已绑定的仓库ID列表
  const [loadingOwnRepos, setLoadingOwnRepos] = useState(false);
  const [searching, setSearching] = useState(false);
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);
  
  const { loading, error, bindRepository, verifyAndGetRepositoryId } = useRepositoryBinding();

  // 获取已绑定的仓库ID列表
  const fetchBoundRepositories = async () => {
    try {
      const response = await backendService.repositories.getBoundRepositories();
      if (response.status === 0 && response.data) {
        const boundIds = response.data.map(repo => repo.id);
        setBoundRepositoryIds(boundIds);
        // 在获取到绑定列表后立即尝试加载自有仓库（避免首次点击还没加载的空白状态）
        if (ownRepositories.length === 0) {
          fetchOwnRepositories(boundIds); // 传入最新的绑定ID列表
        }
      }
    } catch (error) {
      console.error('Failed to fetch bound repositories:', error);
    }
  };

  // 获取用户拥有的GitLab仓库
  const fetchOwnRepositories = async (overrideBoundIds) => {
    setLoadingOwnRepos(true);
    try {
      const repos = await gitlabService.getProjects({ owned: true, per_page: 20 });
      // 过滤掉已绑定的仓库
      const boundIdsRef = overrideBoundIds || boundRepositoryIds; // 支持提前传入的绑定ID（状态尚未来得及更新）
      const unboundRepos = repos.filter(repo => !boundIdsRef.includes(repo.id));
      setOwnRepositories(unboundRepos);
    } catch (error) {
      console.error('Failed to fetch own repositories:', error);
    } finally {
      setLoadingOwnRepos(false);
    }
  };

  // 搜索公开仓库
  const searchRepositories = async (query) => {
    const searchQuery = query.split('/').pop(); // 只使用/后的部分进行搜索
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    setSearching(true);
    try {
      const repos = await gitlabService.getProjects({ search: searchQuery, per_page: 10 });
      const filteredRepos = repos.filter(repo => 
        repo.path_with_namespace.toLowerCase().includes(query.toLowerCase()) &&
        !boundRepositoryIds.includes(repo.id) // 过滤掉已绑定的仓库
      );
      setSearchResults(filteredRepos);
    } catch (error) {
      console.error('Failed to search repositories:', error);
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  };

  // 初始化时获取已绑定的仓库列表
  useEffect(() => {
    fetchBoundRepositories();
  }, []);

  // 如果 1 秒后仍未加载用户仓库且用户未输入内容，则自动尝试加载一次，提升首次体验
  useEffect(() => {
    if (ownRepositories.length === 0 && !loadingOwnRepos) {
      const timer = setTimeout(() => {
        if (ownRepositories.length === 0 && !loadingOwnRepos) {
          fetchOwnRepositories();
        }
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [ownRepositories.length, loadingOwnRepos]);

  // 处理输入变化
  const handleInputChange = (e) => {
    const value = e.target.value;
    setInputValue(value);
    setSelectedRepository(null);
    
    if (value.trim()) {
      // 延迟搜索
      const timer = setTimeout(() => {
        searchRepositories(value);
      }, 300);
      return () => clearTimeout(timer);
    } else {
      setSearchResults([]);
    }
  };

  // 处理输入框聚焦
  const handleInputFocus = () => {
    setShowDropdown(true);
    // 之前限制必须已绑定仓库才加载，这会导致首次进入为空；现在只要还没加载就拉取
    if (ownRepositories.length === 0 && !loadingOwnRepos) {
      fetchOwnRepositories();
    }
  };

  // 处理点击外部关闭下拉框
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // 选择仓库
  const handleSelectRepository = (repo) => {
    setSelectedRepository(repo);
    setInputValue(repo.path_with_namespace);
    setShowDropdown(false);
  };

  // 绑定仓库
  const handleBindRepository = async () => {
    if (!selectedRepository) {
      // 如果没有选中仓库，尝试通过输入框内容验证
      if (!inputValue.trim()) return;
      
      const repoId = await verifyAndGetRepositoryId(inputValue.trim());
      if (!repoId) return;
      
      const success = await bindRepository(repoId);
      if (success) {
        setInputValue('');
        setSelectedRepository(null);
        // 重新获取已绑定的仓库列表并刷新界面
        await fetchBoundRepositories();
        onRepositoryBound();
      }
    } else {
      // 使用选中的仓库
      const success = await bindRepository(selectedRepository.id);
      if (success) {
        setInputValue('');
        setSelectedRepository(null);
        // 重新获取已绑定的仓库列表并刷新界面
        await fetchBoundRepositories();
        onRepositoryBound();
      }
    }
  };

  // 处理回车键
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (selectedRepository) {
        handleBindRepository();
      } else if (searchResults.length > 0) {
        handleSelectRepository(searchResults[0]);
      }
    }
  };

  return (
    <div className={styles.repositoryBindingContainer}>
      <div className={styles.bindingInputContainer} ref={dropdownRef}>
        <div className={styles.inputWrapper}>
          <div className={styles.inputHeader}>
            <h2>添加仓库</h2>
          </div>
          <div className={styles.searchInputGroup}>
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={handleInputChange}
              onFocus={handleInputFocus}
              onKeyPress={handleKeyPress}
              placeholder="搜索或输入仓库名称 (例如: repository)"
              className={styles.repositorySearchInput}
            />
            <button
              onClick={handleBindRepository}
              disabled={loading || (!selectedRepository && !inputValue.trim())}
              className={styles.bindActionButton}
            >
              {loading ? '绑定中...' : '绑定'}
            </button>
          </div>
          
          {error && (
            <div className={styles.errorMessage}>
              {error}
            </div>
          )}
        </div>

        {showDropdown && (
          <div className={styles.repositoryDropdown}>
            {inputValue.trim() ? (
              // 显示搜索结果
              <div className={styles.dropdownSection}>
                <div className={styles.sectionHeader}>
                  {searching ? '搜索中...' : '搜索结果'}
                </div>
                {searchResults.length > 0 ? (
                  searchResults.map((repo) => (
                    <div
                      key={repo.id}
                      className={`${styles.repositoryOption} ${
                        selectedRepository?.id === repo.id ? styles.selected : ''
                      }`}
                      onClick={() => handleSelectRepository(repo)}
                    >
                      <div className={styles.repoInfo}>
                        <div className={styles.repoName}>{repo.path_with_namespace}</div>
                        <div className={styles.repoMeta}>
                          <span className={styles.visibility}>{repo.visibility}</span>
                          {repo.description && (
                            <span className={styles.description}>{repo.description}</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  !searching && (
                    <div className={styles.emptyState}>
                      {boundRepositoryIds.length > 0 
                        ? '没有找到匹配的未绑定仓库'
                        : '没有找到匹配的仓库'
                      }
                    </div>
                  )
                )}
              </div>
            ) : (
              // 显示用户拥有的仓库
              <div className={styles.dropdownSection}>
                <div className={styles.sectionHeader}>
                  {loadingOwnRepos ? '加载中...' : '我的仓库'}
                </div>
                {ownRepositories.length > 0 ? (
                  ownRepositories.map((repo) => (
                    <div
                      key={repo.id}
                      className={`${styles.repositoryOption} ${
                        selectedRepository?.id === repo.id ? styles.selected : ''
                      }`}
                      onClick={() => handleSelectRepository(repo)}
                    >
                      <div className={styles.repoInfo}>
                        <div className={styles.repoName}>{repo.path_with_namespace}</div>
                        <div className={styles.repoMeta}>
                          <span className={styles.visibility}>{repo.visibility}</span>
                          {repo.description && (
                            <span className={styles.description}>{repo.description}</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  !loadingOwnRepos && (
                    <div className={styles.emptyState}>
                      {boundRepositoryIds.length > 0 
                        ? '所有您拥有的仓库都已绑定，或者您可以搜索其他仓库'
                        : '没有找到您拥有的仓库'
                      }
                    </div>
                  )
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default RepositoryBinding;
